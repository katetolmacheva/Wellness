"use client";

import Link from "next/link";
import styles from "../profile.module.css";
import { useState } from "react";

type Role = "user" | "expert";


function ArrowLeftIcon() {
    return (
        <svg width="58" height="24" viewBox="0 0 58 24" fill="none">
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

function PencilLineIcon() {
    return (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path
                d="M15 5L19 9"
                stroke="currentColor"
                strokeWidth="1.7"
                strokeLinecap="round"
                strokeLinejoin="round"
            />
            <path
                d="M5 19L9.5 18L18 9.5L14.5 6L6 14.5L5 19Z"
                stroke="currentColor"
                strokeWidth="1.7"
                strokeLinecap="round"
                strokeLinejoin="round"
            />
        </svg>
    );
}

function PlusIcon() {
    return <span className={styles.plusIcon}>+</span>;
}

export default function ProfileSettingsPage() {
    const [role] = useState<Role>("expert");

    const favoriteTopics = [
        "Йога",
        "Спорт",
        "Правильно питание",
        "Витамины и БАДы",
        "Профилактика",
        "Сон",
        "Здоровое старение",
        "Витамины и БАДы",
        "Витамины и БАДы",
        "Витамины и БАДы",
    ];

    const docs = [
        "/images/articles/img_нарушения-сна-у-жителей-мегаполиса_65237053.png",
        "/images/articles/img_нарушения-сна-у-жителей-мегаполиса_65237053.png",
    ];

    const [logoutOpen, setLogoutOpen] = useState(false);
    const [deleteOpen, setDeleteOpen] = useState(false);

    return (
        <div className={styles.page}>
            <header className={styles.topbar}>
                <div className={styles.topbarLeft}>
                    <nav className={styles.tabs}>
                        <Link href="/feed" className={styles.tab}>Feed</Link>
                        <Link href="/ai" className={styles.tab}>Chat</Link>
                    </nav>

                    <Link href="/profile" className={styles.backBtn}>
                        <ArrowLeftIcon />
                    </Link>
                </div>
            </header>

            <main className={styles.container}>

                <section className={styles.settingsHead}>
                    <div className={styles.settingsAvatar}></div>

                    <div className={styles.settingsHeadInfo}>
                        <div className={styles.inlineInput}>
                            <input defaultValue="Татьяна" className={styles.ghostInput} />
                        </div>

                        <div className={styles.birthText}>13.05.2002</div>
                    </div>
                </section>

                <section className={styles.settingsForm}>
                    <div className={styles.editField}>
                        <span className={styles.fieldText}>Oreshki.big.Bob@gmail.com</span>
                        <button type="button" className={styles.fieldEditBtn} aria-label="Редактировать email">
                            <PencilLineIcon />
                        </button>
                    </div>

                    <div className={styles.editField}>
                        <span className={styles.fieldText}>................</span>
                        <button type="button" className={styles.fieldEditBtn} aria-label="Редактировать пароль">
                            <PencilLineIcon />
                        </button>
                    </div>
                </section>

                <section className={styles.topicsSettingsSection}>
                    <div className={styles.sectionLabel}>Любимые темы:</div>
                    <div className={styles.topicList}>
                        {favoriteTopics.map((topic, i) => (
                            <span key={`${topic}-${i}`} className={styles.topicPillDark}>
                {topic}
              </span>
                        ))}
                        <button className={styles.addTopicBtn} type="button" aria-label="Добавить тему">
                            <PlusIcon />
                        </button>
                    </div>
                </section>

                {role === "user" && (
                    <section className={styles.verifyBlock}>
                        <h2 className={styles.verifyTitle}>Сейчас вы — пользователь платформы.</h2>

                        <div className={styles.roleSwitch}>
                            <span className={`${styles.switchBtn} ${styles.switchBtnActive}`}>Пользователь</span>
                            <span className={styles.switchBtn}>Эксперт</span>
                        </div>

                        <p className={styles.verifyText}>
                            Чтобы публиковать собственные статьи, нужно
                            <br />
                            прикрепить несколько документов на проверку.
                        </p>

                        <div className={styles.uploadStub}>
                            Прикрепите копию вашего диплома или других документов,
                            <br />
                            подтверждающих, что вам можно доверять
                        </div>

                        <button className={styles.primaryWideBtn} type="button">
                            Подтвердить экспертность
                        </button>
                    </section>
                )}

                {role === "expert" && (
                    <section className={styles.verifyBlock}>
                        <h2 className={styles.verifyTitle}>Вы — эксперт платформы.</h2>

                        <div className={styles.docsBox}>
                            <div className={styles.docsLabel}>Ваши документы:</div>

                            <div className={styles.docsRow}>
                                {docs.map((doc, i) => (
                                    <div key={i} className={styles.docItem}>
                                        <img src={doc} alt={`Документ ${i + 1}`} className={styles.docImage} />
                                    </div>
                                ))}

                                <button type="button" className={styles.docAddBtn} aria-label="Добавить документ">
                                    <PlusIcon />
                                </button>
                            </div>
                        </div>
                    </section>
                )}

                <div className={styles.bottomActions}>
                    <button
                        className={styles.secondaryWideBtn}
                        type="button"
                        onClick={() => setLogoutOpen(true)}
                    >
                        Выйти
                    </button>

                    <button
                        className={styles.deleteBtn}
                        type="button"
                        onClick={() => setDeleteOpen(true)}
                    >
                        Удалить аккаунт
                    </button>
                </div>
                {logoutOpen && (
                    <div className={styles.modalOverlay} onClick={() => setLogoutOpen(false)}>
                        <div
                            className={styles.logoutModal}
                            onClick={(e) => e.stopPropagation()}
                        >
                            <p className={styles.logoutModalText}>
                                Вы уверены, что хотите выйти?
                            </p>

                            <button
                                type="button"
                                className={styles.logoutConfirmBtn}
                                onClick={() => {
                                    setLogoutOpen(false);
                                    // сюда потом добавишь реальный logout
                                    // например:
                                    // router.push("/login");
                                }}
                            >
                                Да, выйти
                            </button>

                            <button
                                type="button"
                                className={styles.logoutCancelBtn}
                                onClick={() => setLogoutOpen(false)}
                            >
                                Вернуться в профиль
                            </button>
                        </div>
                    </div>
                )}
                {deleteOpen && (
                    <div className={styles.modalOverlay} onClick={() => setDeleteOpen(false)}>
                        <div
                            className={styles.logoutModal}
                            onClick={(e) => e.stopPropagation()}
                        >
                            <p className={styles.logoutModalText}>
                                Вы уверены, что хотите удалить аккаунт?
                            </p>

                            <button
                                type="button"
                                className={styles.logoutConfirmBtn}
                                onClick={() => {
                                    setDeleteOpen(false);
                                    // здесь потом API удаления аккаунта
                                }}
                            >
                                Да, удалить
                            </button>

                            <button
                                type="button"
                                className={styles.logoutCancelBtn}
                                onClick={() => setDeleteOpen(false)}
                            >
                                Отмена
                            </button>
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}