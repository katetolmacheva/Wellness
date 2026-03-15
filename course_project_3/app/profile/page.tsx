"use client";

import Link from "next/link";
import styles from "./profile.module.css";
import { useMemo, useState } from "react";

type Role = "user" | "expert";

type ProfileArticle = {
    id: string;
    title: string;
    image: string;
    tags: string[];
    author?: string;
    date?: string;
    views?: number;
    updatedText?: string;
};

function ArrowLeftIcon() {
    return (
        <svg width="58" height="24" viewBox="0 0 58 24" fill="none" aria-hidden="true">
            <path
                d="M56 12H14"
                stroke="currentColor"
                strokeWidth="2.5"
                strokeLinecap="round"
            />
            <path
                d="M14 12L24 2"
                stroke="currentColor"
                strokeWidth="2.5"
                strokeLinecap="round"
            />
            <path
                d="M14 12L24 22"
                stroke="currentColor"
                strokeWidth="2.5"
                strokeLinecap="round"
            />
        </svg>
    );
}

function GearIcon() {
    return (
        <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
            <path d="M19.14 12.94c.04-.31.06-.63.06-.94s-.02-.63-.06-.94l2.03-1.58a.5.5 0 0 0 .12-.64l-1.92-3.32a.5.5 0 0 0-.6-.22l-2.39.96a7.3 7.3 0 0 0-1.63-.94l-.36-2.54a.5.5 0 0 0-.5-.42h-3.84a.5.5 0 0 0-.5.42l-.36 2.54c-.58.22-1.13.53-1.63.94l-2.39-.96a.5.5 0 0 0-.6.22L2.65 8.84a.5.5 0 0 0 .12.64L4.8 11.06c-.04.31-.06.63-.06.94s.02.63.06.94l-2.03 1.58a.5.5 0 0 0-.12.64l1.92 3.32a.5.5 0 0 0 .6.22l2.39-.96c.5.41 1.05.72 1.63.94l.36 2.54a.5.5 0 0 0 .5.42h3.84a.5.5 0 0 0 .5-.42l.36-2.54c.58-.22 1.13-.53 1.63-.94l2.39.96a.5.5 0 0 0 .6-.22l1.92-3.32a.5.5 0 0 0-.12-.64l-2.03-1.58ZM12 15.5A3.5 3.5 0 1 1 12 8.5a3.5 3.5 0 0 1 0 7Z" />
        </svg>
    );
}

function SearchIcon() {
    return (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <circle cx="11" cy="11" r="6.5" stroke="currentColor" strokeWidth="1.8" />
            <path d="M16 16L20 20" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
        </svg>
    );
}

function PlusIcon() {
    return <span className={styles.plusIcon}>+</span>;
}

function StatArticleCard({
                             article,
                             compact = false,
                             activeTag,
                         }: {
    article: ProfileArticle;
    compact?: boolean;
    activeTag: string;
}) {
    return (
        <article className={`${styles.articleCard} ${compact ? styles.articleCardCompact : ""}`}>
            <div className={styles.articleImageWrap}>
                <img src={article.image} alt={article.title} className={styles.articleImage} />
            </div>

            <h3 className={styles.articleTitle}>{article.title}</h3>

            <div className={styles.cardTagsPills}>
                {article.tags.map((tag) => {
                    const isActive =
                        activeTag !== "все" &&
                        tag.toLowerCase() === activeTag.toLowerCase();

                    return (
                        <span
                            key={tag}
                            className={`${styles.cardTagPill} ${isActive ? styles.cardTagPillActive : ""}`}
                        >
                {tag}
            </span>
                    );
                })}
            </div>

            <div className={styles.articleMetaInline}>
                <span>{article.author ?? "Е.В. Царева"}</span>
                <span className={styles.metaDot}>•</span>
                <span>{article.date ?? "14 марта 2026 г."}</span>
            </div>
        </article>
    );
}


export default function ProfilePage() {
    const [role] = useState<Role>("expert");
    const [tab, setTab] = useState<"saved" | "created">("created");
    const [search, setSearch] = useState("");
    const [activeTag, setActiveTag] = useState("все");


    const favoriteTopics = [
        "Йога",
        "Спорт",
        "Правильно питание",
        "Витамины и БАДы",
        "Витамины и БАДы",
    ];

    const filterTags = ["все", "гибкость", "бодрость", "витамины", "ментальное здоровье"];

    const savedArticles: ProfileArticle[] = [
        {
            id: "1",
            title: "НАРУШЕНИЕ СНА ПРИ РАССТРОЙСТВЕ АДАПТАЦИИ",
            image: "/images/articles/img_нарушения-сна-у-жителей-мегаполиса_65237053.png",
            tags: ["сон", "бессонница", "бодрость", "нервная система"],
            author: "Мария Петрова",
            date: "13 января 2024",
        },
        {
            id: "2",
            title: "ДИФФЕРЕНЦИАЛЬНАЯ ДИАГНОСТИКА",
            image: "/images/articles/img_нарушения-сна-у-жителей-мегаполиса_65237053.png",
            tags: ["сон", "бессонница", "диагностика"],
            author: "Мария Петрова",
            date: "13 января 2024",
        },
        {
            id: "3",
            title: "ЙОГА ДЛЯ НАЧИНАЮЩИХ: ПЕРВЫЕ ШАГИ К ГАРМОНИИ",
            image: "/images/articles/img_нарушения-сна-у-жителей-мегаполиса_65237053.png",
            tags: ["сон", "йога", "бодрость", "утренняя зарядка"],
            author: "Мария Петрова",
            date: "13 января 2024",
        },
        {
            id: "4",
            title: "НАРУШЕНИЯ СНА У ЖИТЕЛЕЙ МЕГАПОЛИСА",
            image: "/images/articles/img_нарушения-сна-у-жителей-мегаполиса_65237053.png",
            tags: ["сон", "бессонница", "нарушения"],
            author: "Мария Петрова",
            date: "13 января 2024",
        },
        {
            id: "5",
            title: "ПСИХИЧЕСКОЕ ЗДОРОВЬЕ НАСЕЛЕНИЯ",
            image: "/images/articles/img_нарушения-сна-у-жителей-мегаполиса_65237053.png",
            tags: ["сон", "психология", "бодрость"],
            author: "Мария Петрова",
            date: "13 января 2024",
        },
    ];

    const createdArticles: ProfileArticle[] = [
        {
            id: "c1",
            title: "ВСЕ СТАТЬИ",
            image: "/images/articles/img_нарушения-сна-у-жителей-мегаполиса_65237053.png",
            tags: ["йога", "гибкость", "бодрость", "утренняя зарядка", "..."],
            date: "14 августа 2024",
        },
        {
            id: "c2",
            title: "ПРАВИЛЬНЫЙ СОН",
            image: "/images/articles/img_нарушения-сна-у-жителей-мегаполиса_65237053.png",
            tags: ["сон", "мелатонин", "бодрость", "спокойствие", "бессонница"],
            date: "14 августа 2024",
        },
        {
            id: "c3",
            title: "ПРАВИЛЬНЫЙ СОН",
            image: "/images/articles/img_нарушения-сна-у-жителей-мегаполиса_65237053.png",
            tags: ["сон", "мелатонин", "бодрость", "спокойствие", "бессонница"],
            date: "14 августа 2024",
        },
        {
            id: "c4",
            title: "ПРАВИЛЬНЫЙ СОН",
            image: "/images/articles/img_нарушения-сна-у-жителей-мегаполиса_65237053.png",
            tags: ["сон", "мелатонин", "бодрость", "спокойствие", "бессонница"],
            date: "14 августа 2024",
        },
        {
            id: "c5",
            title: "ПРАВИЛЬНЫЙ СОН",
            image: "/images/articles/img_нарушения-сна-у-жителей-мегаполиса_65237053.png",
            tags: ["сон", "мелатонин", "бодрость", "спокойствие", "бессонница"],
            date: "14 августа 2024",
        },
    ];

    const filterArticles = (articles: ProfileArticle[]) => {
        return articles.filter((article) => {
            const matchesSearch =
                search.trim() === "" ||
                article.title.toLowerCase().includes(search.toLowerCase()) ||
                article.tags.some((tag) => tag.toLowerCase().includes(search.toLowerCase()));

            const matchesTag =
                activeTag === "все" ||
                article.tags.some((tag) => tag.toLowerCase() === activeTag.toLowerCase());

            return matchesSearch && matchesTag;
        });
    };

    const filteredSavedArticles = filterArticles(savedArticles);
    const filteredCreatedArticles = filterArticles(createdArticles);

    const createdActionText = role === "expert" ? "МОИ СТАТЬИ" : "";
    const shouldShowCreatedGrid = role === "expert";

    const mainTitle = useMemo(() => {
        if (tab === "saved") return "МОИ ПОДБОРКИ";
        if (role === "expert") return "МОИ СТАТЬИ";
        return "";
    }, [tab, role]);

    return (
        <div className={styles.page}>
            <header className={styles.topbar}>
                <div className={styles.topbarLeft}>
                    <nav className={styles.tabs}>
                        <Link href="/feed" className={styles.tab}>Feed</Link>
                        <Link href="/ai" className={styles.tab}>Chat</Link>
                    </nav>

                    <Link href="/" className={styles.backBtn} aria-label="Назад">
                        <ArrowLeftIcon />
                    </Link>
                </div>

                <div className={styles.topActions}>
                    <Link href="/profile/settings" className={styles.settingsBtn} aria-label="Настройки">
                        <GearIcon />
                    </Link>
                </div>
            </header>

            <main className={styles.container}>

                <section className={styles.profileHead}>
                    <div className={styles.avatar}></div>
                    <h1 className={styles.userName}>Татьяна</h1>
                    {role === "expert" ? (
                        <span className={styles.roleBadge}>Эксперт</span>
                    ) : (
                        <span className={styles.userRole}>Пользователь</span>
                    )}
                </section>

                <section className={styles.topicsSection}>
                    <div className={styles.sectionLabel}>Любимые темы:</div>
                    <div className={styles.topicList}>
                        {favoriteTopics.map((topic, i) => (
                            <span key={`${topic}-${i}`} className={styles.topicPill}>
                {topic}
              </span>
                        ))}
                        <button className={styles.addTopicBtn} type="button" aria-label="Добавить тему">
                            <PlusIcon />
                        </button>
                    </div>
                </section>

                <section className={styles.switchRow}>
                    <button
                        type="button"
                        className={`${styles.switchBtn} ${tab === "saved" ? styles.switchBtnActive : ""}`}
                        onClick={() => setTab("saved")}
                    >
                        Сохраненные
                    </button>

                    <button
                        type="button"
                        className={`${styles.switchBtn} ${tab === "created" ? styles.switchBtnActive : ""}`}
                        onClick={() => setTab("created")}
                    >
                        Созданные
                    </button>
                </section>

                {tab === "saved" && (
                    <>
                        <h2 className={styles.contentTitle}>{mainTitle}</h2>

                        <section className={styles.contentArea}>
                            <aside className={styles.filters}>
                                <div className={styles.searchRow}>
                               <span className={styles.searchIcon}>
                                 <SearchIcon />
                               </span>

                                    <input
                                        type="text"
                                        value={search}
                                        onChange={(e) => setSearch(e.target.value)}
                                        placeholder=""
                                        className={styles.searchInput}
                                    />
                                </div>

                                <div className={styles.tags}>
                                    {filterTags.map((tag) => {
                                        const isActive = activeTag === tag;

                                        return (
                                            <button
                                                key={tag}
                                                type="button"
                                                onClick={() => setActiveTag(tag)}
                                                className={`${styles.tag} ${isActive ? styles.tagActive : ""}`}
                                            >
                                                {tag}
                                            </button>
                                        );
                                    })}
                                </div>
                            </aside>

                            <div className={styles.savedGrid}>
                                {filteredSavedArticles.length > 0 ? (
                                    filteredSavedArticles.map((article) => (
                                        <StatArticleCard
                                            key={article.id}
                                            article={article}
                                            compact
                                            activeTag={activeTag}
                                        />
                                    ))
                                ) : (
                                    <div className={styles.noResults}>Ничего не найдено</div>
                                )}
                            </div>
                        </section>
                    </>
                )}

                {tab === "created" && role === "expert" && (
                    <>
                        <h2 className={styles.contentTitle}>{createdActionText}</h2>

                        <section className={styles.contentArea}>
                            <aside className={styles.filters}>
                                <div className={styles.searchRow}>
        <span className={styles.searchIcon}>
            <SearchIcon />
        </span>

                                    <input
                                        type="text"
                                        value={search}
                                        onChange={(e) => setSearch(e.target.value)}
                                        placeholder=""
                                        className={styles.searchInput}
                                    />
                                </div>

                                <div className={styles.tags}>
                                    {filterTags.map((tag) => {
                                        const isActive = activeTag === tag;

                                        return (
                                            <button
                                                key={tag}
                                                type="button"
                                                onClick={() => setActiveTag(tag)}
                                                className={`${styles.tag} ${isActive ? styles.tagActive : ""}`}
                                            >
                                                {tag}
                                            </button>
                                        );
                                    })}
                                </div>
                            </aside>

                            <div className={styles.createdGrid}>
                                {filteredCreatedArticles.length > 0 ? (
                                    filteredCreatedArticles.map((article) => (
                                        <StatArticleCard
                                            key={article.id}
                                            article={article}
                                            compact
                                            activeTag={activeTag}
                                        />
                                    ))
                                ) : (
                                    <div className={styles.noResults}>Ничего не найдено</div>
                                )}

                                <button className={styles.addArticleCard}>
                                    <PlusIcon />
                                </button>
                            </div>
                        </section>
                    </>
                )}

                {tab === "created" && role === "user" && !shouldShowCreatedGrid && (
                    <section className={styles.emptyState}>
                        <h2 className={styles.emptyTitle}>
                            Чтобы публиковать свои статьи на нашей
                            <br />
                            платформе, необходимо подтвердить свою
                            <br />
                            экспертность.
                        </h2>

                        <p className={styles.emptyText}>
                            Просто прикрепите сканы документов, а об
                            <br />
                            остальном мы позаботимся
                        </p>

                        <button className={styles.primaryWideBtn} type="button">
                            Подтвердить экспертность
                        </button>

                        <button className={styles.linkBtn} type="button">
                            Может быть в другой раз
                        </button>
                    </section>
                )}
            </main>
        </div>
    );
}