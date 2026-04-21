const express = require("express");
const prisma = require("../prisma");
const authMiddleware = require("../middleware/auth");

const router = express.Router();

function extractArticleText(content) {
    if (typeof content === "string") return content;
    if (!Array.isArray(content)) return "";

    const parts = [];
    for (const block of content) {
        if (!block || typeof block !== "object") continue;
        if (typeof block.text === "string") parts.push(block.text);
        if (Array.isArray(block.items)) {
            for (const item of block.items) {
                if (typeof item === "string") parts.push(item);
            }
        }
    }
    return parts.join("\n").trim();
}

async function moderateArticleOrThrow(payload) {
    const chatbotBase = (process.env.CHATBOT_URL || "http://localhost:8000").replace(/\/$/, "");
    const contentText = extractArticleText(payload.content);

    const res = await fetch(`${chatbotBase}/article/moderate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            title: payload.title || "",
            category: payload.category || "",
            annotation: payload.annotation || "",
            content_text: contentText,
        }),
    });

    const moderation = await res.json().catch(() => ({}));
    if (!res.ok) {
        const reason = moderation?.detail || moderation?.message || "Сервис модерации недоступен";
        const err = new Error(String(reason));
        err.statusCode = 502;
        throw err;
    }

    return moderation;
}

/**
 * GET /api/articles
 * Список статей (анонс)
 */
router.get("/", async (req, res) => {
    try {
        const articles = await prisma.article.findMany({
            where: { published: true },
            orderBy: { createdAt: "desc" },
            select: {
                id: true,
                title: true,
                slug: true,
                category: true,
                authorName: true,
                annotation: true,
                imageUrl: true,
                imageAlt: true,
                createdAt: true
            }
        });

        res.json(articles);
    } catch (e) {
        console.error(e);
        res.status(500).json({ error: "Failed to load articles" });
    }
});

/**
 * GET /api/articles/id/:id
 */
router.get("/id/:id", async (req, res) => {
    try {
        const article = await prisma.article.findUnique({
            where: { id: req.params.id },
        });

        if (!article || !article.published) return res.status(404).json({ error: "Article not found" });

        res.json(article);
    } catch (e) {
        console.error(e);
        res.status(500).json({ error: "Failed to load article by id" });
    }
});

/**
 * GET /api/articles/:slug
 */
router.get("/:slug", async (req, res) => {
    try {
        const { slug } = req.params;

        const article = await prisma.article.findUnique({
            where: { slug }
        });

        if (!article || !article.published) return res.status(404).json({ error: "Article not found" });

        res.json(article);
    } catch (e) {
        console.error(e);
        res.status(500).json({ error: "Failed to load article by slug" });
    }
});

/**
 * POST /api/articles
 * Создать новую статью (используйте аутентификацию/права на продакшне)
 * Тело: { title, authorName, authorBio?, category, annotation, imageUrl?, imageAlt?, content, sources, published? }
 */
router.post("/", authMiddleware, async (req, res) => {
    try {
        const currentUser = await prisma.user.findUnique({
            where: { id: req.user.userId },
            select: { first_name: true, last_name: true, role: true, is_verified: true, bio: true },
        });

        if (!currentUser) {
            return res.status(401).json({ error: "Пользователь не найден" });
        }

        if (currentUser.role !== "expert" || !currentUser.is_verified) {
            return res.status(403).json({
                error: "Публикация доступна только верифицированным экспертам",
            });
        }

        const payload = req.body || {};
        const title = (payload.title || "").trim();
        if (!title) return res.status(400).json({ error: "Title is required" });

        const moderation = await moderateArticleOrThrow(payload);
        const isApproved = moderation?.decision === "approved";
        if (!isApproved) {
            return res.status(422).json({
                error: "Статья не прошла модерацию",
                moderation: {
                    status: moderation?.decision || "rejected",
                    reasons: Array.isArray(moderation?.reasons) ? moderation.reasons : [],
                    red_flags: Array.isArray(moderation?.red_flags) ? moderation.red_flags : [],
                    confidence_score: moderation?.confidence_score ?? null,
                },
            });
        }

        // простая slugify
        const slugBase = String(title).toLowerCase()
            .replace(/ё/g, "е")
            .replace(/[^a-zа-я0-9]+/gi, "-")
            .replace(/^-+|-+$/g, "");

        // проверяем уникальность slug, добавляем суффикс при конфликте
        let slug = slugBase || `${Date.now()}`;
        let counter = 0;
        while (true) {
            const exists = await prisma.article.findUnique({ where: { slug } });
            if (!exists) break;
            counter += 1;
            slug = `${slugBase}-${counter}`;
            if (counter > 1000) break;
        }

        const articleData = {
            id: payload.id || undefined, // Prisma сгенерирует uuid если опустить
            title,
            slug,
            authorName: payload.authorName || `${currentUser.first_name || ""} ${currentUser.last_name || ""}`.trim() || "Эксперт",
            authorBio: payload.authorBio || currentUser.bio || null,
            category: payload.category || "Новости",
            annotation: payload.annotation || "",
            imageUrl: payload.imageUrl || "/images/articles/placeholder.png",
            imageAlt: payload.imageAlt || title,
            content: Array.isArray(payload.content) ? payload.content : [],
            sources: Array.isArray(payload.sources) ? payload.sources : [],
            published: true,
            moderationStatus: "approved",
            moderationReason: Array.isArray(moderation?.reasons) ? moderation.reasons.join("; ").slice(0, 1000) : null,
            moderationScore: Number.isInteger(moderation?.confidence_score) ? moderation.confidence_score : null,
            moderatedAt: new Date(),
        };

        const created = await prisma.article.create({ data: articleData });

        res.status(201).json(created);
    } catch (e) {
        console.error(e);
        res.status(500).json({ error: "Failed to create article" });
    }
});

module.exports = router;