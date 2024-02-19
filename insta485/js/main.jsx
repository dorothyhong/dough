// import React, { StrictMode } from "react";
// import { createRoot } from "react-dom/client";
// import Post from "./post";

// // Create a root
// const root = createRoot(document.getElementById("reactEntry"));

// // This method is only called once
// // Insert the post component into the DOM
// root.render(
//   <StrictMode>
//     <Post url="/api/v1/posts/1/" />
//   </StrictMode>
// );

import React, { StrictMode, useState, useEffect } from "react";
import { createRoot } from "react-dom/client";
import Post from "./post";

// Create a root
const root = createRoot(document.getElementById("reactEntry"));

function Main() {
  const [posts, setPosts] = useState([]);

  useEffect(() => {
    // Fetch data for multiple posts
    fetch("/api/v1/posts/") // Assuming this endpoint returns data for multiple posts
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        setPosts(data.results); // Assuming data.results contains an array of posts
      })
      .catch((error) => console.log(error));
  }, []);

  return (
    <div>
      {posts.map((post) => (
        <Post key={post.postid} url={post.url} postId={post.postid} />
      ))}
    </div>
  );
}

// This method is only called once
// Insert the Main component into the DOM
root.render(
  <StrictMode>
    <Main />
  </StrictMode>
);
