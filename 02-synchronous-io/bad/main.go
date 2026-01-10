package main

import (
"context"
"encoding/json"
"fmt"
"log"
"net/http"
"time"
)

// BAD: Synchronous I/O - blocking on each operation

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
}

// ANTIPATTERN: Sequential, blocking API calls
func getAggregatedProfile(userID int) (*UserProfile, error) {
	ctx := context.Background()

	// Call 1: Fetch user (blocks for ~500ms)
	user, err := fetchUser(ctx, userID)
	if err != nil {
		return nil, err
	}

	// Call 2: Fetch posts (blocks for ~500ms) - waits for Call 1 to complete
	posts, err := fetchPosts(ctx, userID)
	if err != nil {
		return nil, err
	}

	// Call 3: Fetch comments (blocks for ~500ms) - waits for Call 2 to complete
	comments, err := fetchComments(ctx, userID)
	if err != nil {
		return nil, err
	}

	// Total time: ~1500ms (500ms + 500ms + 500ms)
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
	// Fetch comments for user's first post
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

profile, err := getAggregatedProfile(1)
if err != nil {
http.Error(w, err.Error(), http.StatusInternalServerError)
return
}

duration := time.Since(start)
log.Printf("❌ Request took: %v (sequential blocking calls)", duration)

w.Header().Set("Content-Type", "application/json")
w.Header().Set("X-Duration-Ms", fmt.Sprintf("%d", duration.Milliseconds()))
json.NewEncoder(w).Encode(profile)
}

func main() {
http.HandleFunc("/aggregate", aggregateHandler)

fmt.Println("❌ BAD: Server starting on :8082")
fmt.Println("This server demonstrates SYNCHRONOUS I/O antipattern:")
fmt.Println("- Makes 3 API calls sequentially (blocking)")
fmt.Println("- Each call waits for the previous to complete")
fmt.Println("- Total latency = sum of all call latencies")
fmt.Println("\nTry: curl http://localhost:8082/aggregate")
fmt.Println("Watch the X-Duration-Ms header (should be ~1500ms+)")

log.Fatal(http.ListenAndServe(":8082", nil))
}
