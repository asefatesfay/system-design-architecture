package main

import (
"context"
"encoding/json"
"fmt"
"log"
"net/http"
"sync"
"time"
)

// GOOD: Asynchronous I/O - concurrent operations with goroutines

type UserProfile struct {
	User     User      `json:"user"`
	Posts    []Post    `json:"posts"`
	Comments []Comment `json:"comments"`
}

type User struct {
	ID    int    `json:"id"`
	Name  string `json:"name"`
	Email string `json:"email"`
}

type Post struct {
	ID     int    `json:"id"`
	Title  string `json:"title"`
	Body   string `json:"body"`
}

type Comment struct {
	ID   int    `json:"id"`
	Name string `json:"name"`
	Body string `json:"body"`
}

var httpClient = &http.Client{
	Timeout: 30 * time.Second,
	Transport: &http.Transport{
		MaxIdleConns:        100,
		MaxIdleConnsPerHost: 100,
		IdleConnTimeout:     90 * time.Second,
	},
}

// GOOD: Concurrent, non-blocking API calls using goroutines
func getAggregatedProfile(ctx context.Context, userID int) (*UserProfile, error) {
	var (
user     *User
posts    []Post
comments []Comment
wg       sync.WaitGroup
mu       sync.Mutex
errs     []error
)

	// Launch all 3 API calls concurrently
	wg.Add(3)

	// Goroutine 1: Fetch user
	go func() {
		defer wg.Done()
		u, err := fetchUser(ctx, userID)
		mu.Lock()
		defer mu.Unlock()
		if err != nil {
			errs = append(errs, err)
		} else {
			user = u
		}
	}()

	// Goroutine 2: Fetch posts (runs in parallel with user fetch)
	go func() {
		defer wg.Done()
		p, err := fetchPosts(ctx, userID)
		mu.Lock()
		defer mu.Unlock()
		if err != nil {
			errs = append(errs, err)
		} else {
			posts = p
		}
	}()

	// Goroutine 3: Fetch comments (runs in parallel with other fetches)
	go func() {
		defer wg.Done()
		c, err := fetchComments(ctx, userID)
		mu.Lock()
		defer mu.Unlock()
		if err != nil {
			errs = append(errs, err)
		} else {
			comments = c
		}
	}()

	// Wait for all goroutines to complete
	wg.Wait()

	// Check for errors
	if len(errs) > 0 {
		return nil, errs[0]
	}

	// Total time: ~500ms (max of all concurrent calls, not sum)
	return &UserProfile{
		User:     *user,
		Posts:    posts,
		Comments: comments,
	}, nil
}

func fetchUser(ctx context.Context, userID int) (*User, error) {
	url := fmt.Sprintf("https://jsonplaceholder.typicode.com/users/%d", userID)
	req, _ := http.NewRequestWithContext(ctx, "GET", url, nil)

	resp, err := httpClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var user User
	if err := json.NewDecoder(resp.Body).Decode(&user); err != nil {
		return nil, err
	}

	return &user, nil
}

func fetchPosts(ctx context.Context, userID int) ([]Post, error) {
	url := fmt.Sprintf("https://jsonplaceholder.typicode.com/posts?userId=%d", userID)
	req, _ := http.NewRequestWithContext(ctx, "GET", url, nil)

	resp, err := httpClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var posts []Post
	if err := json.NewDecoder(resp.Body).Decode(&posts); err != nil {
		return nil, err
	}

	return posts, nil
}

func fetchComments(ctx context.Context, userID int) ([]Comment, error) {
	url := fmt.Sprintf("https://jsonplaceholder.typicode.com/comments?postId=%d", userID)
	req, _ := http.NewRequestWithContext(ctx, "GET", url, nil)

	resp, err := httpClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var comments []Comment
	if err := json.NewDecoder(resp.Body).Decode(&comments); err != nil {
		return nil, err
	}

	return comments, nil
}

func aggregateHandler(w http.ResponseWriter, r *http.Request) {
	start := time.Now()

	profile, err := getAggregatedProfile(r.Context(), 1)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	duration := time.Since(start)
	log.Printf("✅ Request took: %v (concurrent non-blocking calls)", duration)

	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("X-Duration-Ms", fmt.Sprintf("%d", duration.Milliseconds()))
	json.NewEncoder(w).Encode(profile)
}

func main() {
	http.HandleFunc("/aggregate", aggregateHandler)

	fmt.Println("✅ GOOD: Server starting on :8083")
	fmt.Println("This server demonstrates ASYNCHRONOUS I/O:")
	fmt.Println("- Makes 3 API calls concurrently (non-blocking)")
	fmt.Println("- All calls execute in parallel")
	fmt.Println("- Total latency = max of any single call latency")
	fmt.Println("\nTry: curl http://localhost:8083/aggregate")
	fmt.Println("Watch the X-Duration-Ms header (should be ~500-700ms)")
	fmt.Println("\nCompare with bad version - 3x faster!")

	log.Fatal(http.ListenAndServe(":8083", nil))
}
