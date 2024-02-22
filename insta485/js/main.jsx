import React, { StrictMode, useState, useEffect } from "react";
import { createRoot } from "react-dom/client";
import InfiniteScroll from "react-infinite-scroll-component"; // Import InfiniteScroll
import Post from "./post";

// Create a root
const root = createRoot(document.getElementById("reactEntry"));

function Main() {
  const [posts, setPosts] = useState([]);
  const [hasMorePosts, setHasMorePosts] = useState(true); // To keep track of whether there are more posts to load
  const [nextPageUrl, setNextPageUrl] = useState("/api/v1/posts/"); // This should be the initial URL for the first page

  useEffect(() => {
    // Fetch data for multiple posts
    fetch("/api/v1/posts/") // Assuming this endpoint returns data for multiple posts
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        console.log(data);
        setPosts(data.results); // Assuming data.results contains an array of posts
        setNextPageUrl(data.next);
      })
      .catch((error) => console.log(error));
  }, []);

  const loadMorePosts = () => {
    if (nextPageUrl) {
      // Fetch data for the next set of posts
      fetch(nextPageUrl)
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          return response.json();
        })
        .then((data) => {
          console.log(data);
          setPosts([...posts, ...data.results]); // Add new posts to the existing posts
          setNextPageUrl(data.next); // Update with the next URL, or set to null if there are no more posts
          setHasMorePosts(data.next !== ""); // If there's no next URL, there are no more posts to load
        })
        .catch((error) => console.log(error));
    }
  };

  // return (
  //   <div>
  //     {posts.map((post) => (
  //       <Post key={post.postid} url={post.url} postId={post.postid} />
  //     ))}
  //   </div>
  // );

  return (
    <InfiniteScroll
      loader={<div key={0}>Loading...</div>} // This can be any loading indicator
      hasMore={hasMorePosts}
      next={loadMorePosts}
      dataLength={posts.length}
      endMessage={
        <p style={{ textAlign: "center" }}>
          <b>Yay! You have seen it all</b>
        </p>
      }
    >
      {posts.map((post) => (
        <Post key={post.postid} url={post.url} postId={post.postid} />
      ))}
    </InfiniteScroll>
  );
}

// This method is only called once
// Insert the Main component into the DOM
root.render(
  <StrictMode>
    <Main />
  </StrictMode>,
);
