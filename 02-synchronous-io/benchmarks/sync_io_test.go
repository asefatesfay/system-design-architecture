package benchmarks

import (
	"io"
	"net/http"
	"net/http/httptest"
	"sync"
	"testing"
	"time"
)

func setupMockServer() *httptest.Server {
	return httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		time.Sleep(100 * time.Millisecond)
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`{"data": "test"}`))
	}))
}

func BenchmarkSynchronousIO(b *testing.B) {
	server := setupMockServer()
	defer server.Close()
	client := &http.Client{Timeout: 5 * time.Second}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		for j := 0; j < 3; j++ {
			resp, err := client.Get(server.URL)
			if err != nil {
				b.Fatal(err)
			}
			io.ReadAll(resp.Body)
			resp.Body.Close()
		}
	}
}

func BenchmarkAsynchronousIO(b *testing.B) {
	server := setupMockServer()
	defer server.Close()
	client := &http.Client{Timeout: 5 * time.Second}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		var wg sync.WaitGroup
		wg.Add(3)
		for j := 0; j < 3; j++ {
			go func() {
				defer wg.Done()
				resp, err := client.Get(server.URL)
				if err != nil {
					return
				}
				io.ReadAll(resp.Body)
				resp.Body.Close()
			}()
		}
		wg.Wait()
	}
}
