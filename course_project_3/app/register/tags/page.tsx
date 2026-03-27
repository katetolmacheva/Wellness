'use client';

import { useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import styles from './tags.module.css';

type Category = {
    id: number;
    name: string;
    description?: string | null;
};

export default function TagsPage() {
    const router = useRouter();
    const [tags, setTags] = useState<Category[]>([]);
    const [selected, setSelected] = useState<number[]>([]);

    useEffect(() => {
        const loadCategories = async () => {
            try {
                const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/categories`);
                const data = await res.json();

                if (!res.ok) {
                    throw new Error('Не удалось загрузить категории');
                }

                setTags(data);
            } catch (error) {
                console.error('Ошибка загрузки категорий', error);
            }
        };

        void loadCategories();
    }, []);

    const toggle = (id: number) => {
        setSelected((prev) =>
            prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
        );
    };

    const canGo = useMemo(() => selected.length > 0, [selected]);

    const onContinue = async () => {
        if (!selected.length) return;

        try {
            const token = localStorage.getItem('token');

            if (!token) {
                router.push('/login');
                return;
            }

            const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/profile/interests`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({
                    categoryIds: selected,
                }),
            });

            const data = await res.json();

            if (!res.ok) {
                console.error(data.message || 'Не удалось сохранить теги');
                return;
            }

            router.push('/feed');
        } catch (error) {
            console.error('Ошибка при сохранении тегов', error);
        }
    };

    return (
        <div className={styles.container}>
            <div className={styles.content}>
                <h1 className={styles.title}>Выберите, что вас интересует</h1>

                <div className={styles.tagsGrid}>
                    {tags.map((tag) => {
                        const active = selected.includes(tag.id);

                        return (
                            <button
                                key={tag.id}
                                type="button"
                                className={`${styles.tag} ${active ? styles.tagActive : ''}`}
                                onClick={() => toggle(tag.id)}
                            >
                                {tag.name}
                            </button>
                        );
                    })}
                </div>

                <button className={styles.button} onClick={onContinue} disabled={!canGo}>
                    К статьям
                </button>
            </div>
        </div>
    );
}