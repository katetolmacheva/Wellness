const { PrismaClient } = require("@prisma/client");
const fs = require("fs");

const prisma = new PrismaClient();

function slugify(text) {
    return String(text || "")
        .toLowerCase()
        .trim()
        .replace(/ё/g, "е")
        .replace(/[^a-zа-я0-9]+/gi, "-")
        .replace(/^-+|-+$/g, "");
}

function makeUniqueSlugs(articles) {
    const used = new Map();

    return articles.map((a) => {
        const base = a.slug && a.slug.trim() ? a.slug.trim() : slugify(a.title);
        const count = used.get(base) || 0;
        used.set(base, count + 1);

        const uniqueSlug = count === 0 ? base : `${base}-${count + 1}`;

        return {
            ...a,
            slug: uniqueSlug,
            imageUrl: a.imageUrl || `/images/articles/${uniqueSlug}.jpg`,
            imageAlt: a.imageAlt || a.title || uniqueSlug,
            sources: Array.isArray(a.sources) ? a.sources : [],
            content: Array.isArray(a.content) ? a.content : [],
            published: typeof a.published === "boolean" ? a.published : true,
        };
    });
}

async function main() {
    const articlesRaw = JSON.parse(fs.readFileSync("./articles.json", "utf-8"));
    const articles = makeUniqueSlugs(articlesRaw);

    for (const article of articles) {
        await prisma.article.upsert({
            where: { slug: article.slug },
            update: {
                title: article.title,
                authorName: article.authorName,
                authorBio: article.authorBio || null,
                category: article.category,
                annotation: article.annotation,
                imageUrl: article.imageUrl,
                imageAlt: article.imageAlt,
                content: article.content,
                sources: article.sources,
                published: article.published,
            },
            create: article,
        });
    }

    console.log(`Залито/обновлено статей: ${articles.length}`);
}

main()
    .catch((e) => {
        console.error(e);
        process.exit(1);
    })
    .finally(async () => {
        await prisma.$disconnect();
    });