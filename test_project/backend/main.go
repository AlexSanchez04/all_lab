package main

import (
	"context"
	"encoding/json"
	"errors"
	"log"
	"net/http"
	"os"
	"strconv"
	"strings"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
)

type createNoteRequest struct {
	Title   string `json:"title"`
	Content string `json:"content"`
}

func writeJSON(w http.ResponseWriter, status int, payload any) {
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(payload)
}

func handleHealth(w http.ResponseWriter, r *http.Request) {
	writeJSON(w, http.StatusOK, map[string]string{"status": "ok"})
}

func handleListNotes(pool *pgxpool.Pool) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		notes, err := listNotes(r.Context(), pool)
		if err != nil {
			log.Printf("list notes: %v", err)
			writeJSON(w, http.StatusInternalServerError, map[string]string{"error": "failed to load notes"})
			return
		}
		writeJSON(w, http.StatusOK, notes)
	}
}

func handleGetNote(pool *pgxpool.Pool) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		id, err := strconv.ParseInt(r.PathValue("id"), 10, 64)
		if err != nil {
			writeJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid note id"})
			return
		}
		note, err := getNote(r.Context(), pool, id)
		if err != nil {
			if errors.Is(err, pgx.ErrNoRows) {
				writeJSON(w, http.StatusNotFound, map[string]string{"error": "note not found"})
				return
			}
			log.Printf("get note: %v", err)
			writeJSON(w, http.StatusInternalServerError, map[string]string{"error": "failed to get note"})
			return
		}
		writeJSON(w, http.StatusOK, note)
	}
}

func handleCreateNote(pool *pgxpool.Pool) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		var req createNoteRequest
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
			writeJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid JSON body"})
			return
		}
		req.Title = trimSpace(req.Title)
		if req.Title == "" {
			writeJSON(w, http.StatusBadRequest, map[string]string{"error": "title is required"})
			return
		}
		note, err := createNote(r.Context(), pool, req.Title, req.Content)
		if err != nil {
			log.Printf("create note: %v", err)
			writeJSON(w, http.StatusInternalServerError, map[string]string{"error": "failed to create note"})
			return
		}
		writeJSON(w, http.StatusCreated, note)
	}
}

func withCORS(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
		if r.Method == http.MethodOptions {
			w.WriteHeader(http.StatusNoContent)
			return
		}
		next.ServeHTTP(w, r)
	})
}

func trimSpace(s string) string {
	return strings.TrimSpace(s)
}

func main() {
	ctx := context.Background()
	pool, err := connectDB(ctx)
	if err != nil {
		log.Fatalf("connect to database: %v", err)
	}
	defer pool.Close()

	mux := http.NewServeMux()
	mux.HandleFunc("GET /health", handleHealth)
	mux.HandleFunc("GET /api/notes", handleListNotes(pool))
	mux.HandleFunc("GET /api/notes/{id}", handleGetNote(pool))
	mux.HandleFunc("POST /api/notes", handleCreateNote(pool))

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	addr := ":" + port
	log.Printf("go backend listening on %s", addr)
	if err := http.ListenAndServe(addr, withCORS(mux)); err != nil {
		log.Fatal(err)
	}
}