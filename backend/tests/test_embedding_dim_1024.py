"""Embedding 维度自检:确保 embedding 列与 bge-m3 (1024-dim) 一致。

直接 `python tests/test_embedding_dim_1024.py` 运行。验证两件事:
1. ORM 模型 / 迁移 SQL 里声明的维度是 1024 (不再有遗留的 512)。
2. bge-m3 经 API 返回的 1024 维向量能真正写进 articles.embedding 列并读回 (端到端,
   不再因维度不符在 db.commit() 崩溃 —— 这正是导致微信图表重绘从未执行的根因)。

根因回顾: 旧列 vector(512) + 配置 bge-m3 (1024维) → 导入时 commit 报错 → session 中毒
(PendingRollback) → 在调 _redraw_article_diagrams 之前 (articles.py:232) 就崩溃,
所以 9 张架构图一张都没重绘。
"""
import asyncio
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_passed = 0
_failed = 0


def check(name, cond, detail=""):
    global _passed, _failed
    if cond:
        _passed += 1
        print(f"  ✓ {name}")
    else:
        _failed += 1
        print(f"  ✗ {name}  {detail}")


def test_declarations_are_1024():
    """模型 + 迁移 SQL 不得再硬编码 512 维。"""
    article_model = open(os.path.join(ROOT, "app/models/article.py")).read()
    add_emb = open(os.path.join(ROOT, "app/migrations/add_embedding.sql")).read()
    mig008 = open(os.path.join(ROOT, "app/migrations/008_embedding_dim_512.sql")).read()

    check("model declares Vector(1024)", "Vector(1024)" in article_model, article_model.split("embedding =")[1][:60] if "embedding =" in article_model else "")
    check("add_embedding.sql uses vector(1024)", "vector(1024)" in add_emb and "vector(512)" not in add_emb)
    check("migration 008 targets vector(1024)", "vector(1024)" in mig008 and "TYPE vector(512)" not in mig008)

    # ponytail: 不允许任何残留的 vector(512) / Vector(512) 声明 (SQL 语句里,注释里的历史描述不算)
    for label, src in (("article.py", article_model), ("add_embedding.sql", add_emb), ("008", mig008)):
        code = re.sub(r"--.*", "", src)  # strip SQL line comments
        bad512 = re.findall(r"[Vv]ector\(512\)", code)
        check(f"{label} has no Vector(512) in code", not bad512, str(bad512))


async def test_roundtrip_1024_vector():
    """1024 维向量写入 articles.embedding 列再读回 —— 真正端到端验证不再维度崩溃。"""
    from app.database import async_session
    from app.models import Article
    from sqlalchemy import text

    async with async_session() as db:
        # 准备一个临时行
        ins = await db.execute(text(
            "INSERT INTO articles (id, title, source_platform, user_id, status) "
            "VALUES (gen_random_uuid(), 'dim self-check', 'wechat', "
            "(SELECT id FROM users LIMIT 1), 'unread') RETURNING id"
        ))
        aid = ins.scalar()
        try:
            vec = "[" + ",".join("0.0" for _ in range(1024)) + "]"
            await db.execute(text(
                "UPDATE articles SET embedding = (:v)::vector WHERE id = :id"
            ), {"v": vec, "id": aid})
            row = (await db.execute(text(
                "SELECT vector_dims(embedding) AS d FROM articles WHERE id = :id"
            ), {"id": aid})).first()
            await db.commit()
            check("1024-dim vector round-trips articles.embedding", row and row.d == 1024,
                  f"got dims={getattr(row, 'd', None)}")

            # 反向: 512 维必须被拒绝 (列已不是 512)
            bad = "[" + ",".join("0.0" for _ in range(512)) + "]"
            raised = False
            try:
                await db.execute(text(
                    "UPDATE articles SET embedding = (:v)::vector WHERE id = :id"
                ), {"v": bad, "id": aid})
                await db.flush()
            except Exception:
                raised = True
                await db.rollback()
            check("512-dim vector rejected by column (enforces 1024)", raised,
                  "512-dim was accepted — column is still 512")
        finally:
            await db.execute(text("DELETE FROM articles WHERE id = :id"), {"id": aid})
            await db.commit()


async def test_bge_m3_returns_1024():
    """配置的 API 嵌入模型确实返回 1024 维 (与列匹配)。"""
    from app.config_manager import get_embedding_config
    import httpx
    cfg = get_embedding_config()
    if cfg.get("provider", "local") == "local" or not (cfg.get("api_key") and cfg.get("api_base")):
        print("  (skip live API check: local provider or no creds)")
        return
    r = httpx.post(cfg["api_base"].rstrip("/") + "/embeddings",
                   headers={"Authorization": f"Bearer {cfg['api_key']}", "Content-Type": "application/json"},
                   json={"model": cfg.get("model"), "input": "dim probe", "encoding_format": "float"},
                   timeout=30)
    emb = (r.json().get("data") or [{}])[0].get("embedding", [])
    check(f"configured embedding model {cfg.get('model')} returns 1024-dim", len(emb) == 1024,
          f"got {len(emb)}-dim")


async def main():
    print("== embedding dimension self-check ==")
    test_declarations_are_1024()
    await test_bge_m3_returns_1024()
    await test_roundtrip_1024_vector()
    print(f"\n{'='*40}\nPassed: {_passed}  Failed: {_failed}")
    sys.exit(0 if _failed == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main())
