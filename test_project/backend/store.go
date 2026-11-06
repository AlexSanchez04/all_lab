package main

import (
	"context"
	"os"

	"github.com/jackc/pgx/v5/pgxpool"
)

func connectDB(ctx context.Context) (*pgxpool.Pool, error) {
	dsn := os.Getenv("DATABASE_URL")
	if dsn == "" {
		dsn = "postgres://postgres:postgres@localhost:5432/notesapp"
	}
	return pgxpool.New(ctx, dsn)
}

func listNotes(ctx context.Context, pool *pgxpool.Pool) ([]Note, error) {
	rows, err := pool.Query(ctx, "SELECT id, title, content, created_at FROM notes ORDER BY created_at DESC, id DESC")
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	notes := make([]Note, 0)
	for rows.Next() {
		var n Note
		if err := rows.Scan(&n.ID, &n.Title, &n.Content, &n.CreatedAt); err != nil {
			return nil, err
		}
		notes = append(notes, n)
	}
	return notes, rows.Err()
}

func getNote(ctx context.Context, pool *pgxpool.Pool, id int64) (*Note, error) {
	var n Note
	err := pool.QueryRow(ctx, "SELECT id, title, content, created_at FROM notes WHERE id = $1", id).
		Scan(&n.ID, &n.Title, &n.Content, &n.CreatedAt)
	if err != nil {
		return nil, err
	}
	return &n, nil
}

func createNote(ctx context.Context, pool *pgxpool.Pool, title, content string) (*Note, error) {
	var n Note
	err := pool.QueryRow(ctx,
		"INSERT INTO notes (title, content) VALUES ($1, $2) RETURNING id, title, content, created_at",
		title, content).
		Scan(&n.ID, &n.Title, &n.Content, &n.CreatedAt)
	if err != nil {
		return nil, err
	}
	return &n, nil
}