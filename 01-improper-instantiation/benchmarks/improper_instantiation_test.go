package benchmarks

import (
	"database/sql"
	"net/http"
	"regexp"
	"testing"
	"time"

	_ "github.com/lib/pq"
)

// Benchmark: Creating DB connection every time (BAD)
func BenchmarkBadDBConnection(b *testing.B) {
	for i := 0; i < b.N; i++ {
		db, err := sql.Open("postgres", "postgres://testuser:testpass@localhost:5432/perftest?sslmode=disable")
		if err != nil {
			b.Fatal(err)
		}
		db.Close()
	}
}

// Benchmark: Reusing DB connection pool (GOOD)
func BenchmarkGoodDBConnection(b *testing.B) {
	db, err := sql.Open("postgres", "postgres://testuser:testpass@localhost:5432/perftest?sslmode=disable")
	if err != nil {
		b.Fatal(err)
	}
	defer db.Close()

	db.SetMaxOpenConns(25)
	db.SetMaxIdleConns(25)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		if err := db.Ping(); err != nil {
			b.Fatal(err)
		}
	}
}

// Benchmark: Creating HTTP client every time (BAD)
func BenchmarkBadHTTPClient(b *testing.B) {
	for i := 0; i < b.N; i++ {
		client := &http.Client{Timeout: 10 * time.Second}
		_ = client
	}
}

// Benchmark: Reusing HTTP client (GOOD)
func BenchmarkGoodHTTPClient(b *testing.B) {
	client := &http.Client{
		Timeout: 10 * time.Second,
		Transport: &http.Transport{
			MaxIdleConns:        100,
			MaxIdleConnsPerHost: 100,
		},
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = client
	}
}

// Benchmark: Compiling regex every time (BAD)
func BenchmarkBadRegexCompile(b *testing.B) {
	email := "test@example.com"
	for i := 0; i < b.N; i++ {
		re, err := regexp.Compile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
		if err != nil {
			b.Fatal(err)
		}
		_ = re.MatchString(email)
	}
}

// Benchmark: Pre-compiled regex (GOOD)
func BenchmarkGoodRegexCompile(b *testing.B) {
	email := "test@example.com"
	re := regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = re.MatchString(email)
	}
}

// Memory allocation benchmark
func BenchmarkBadAllocations(b *testing.B) {
	b.ReportAllocs()
	for i := 0; i < b.N; i++ {
		// Simulating creating new objects
		_ = &http.Client{Timeout: 10 * time.Second}
		_, _ = regexp.Compile(`^[a-z]+$`)
	}
}

func BenchmarkGoodAllocations(b *testing.B) {
	b.ReportAllocs()
	client := &http.Client{Timeout: 10 * time.Second}
	re := regexp.MustCompile(`^[a-z]+$`)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = client
		_ = re
	}
}
