import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import utc from "dayjs/plugin/utc";
import Comments from "./comments";
import Likes from "./likes";

dayjs.extend(relativeTime);
dayjs.extend(utc);

// The parameter of this function is an object with a string called url inside it.
// url is a prop forhfhrt the Post component.
export default function Post({ url }) {
  /* Display image and post owner of a single post */

  const initialLikes = {
    "lognameLikesThis": true,
    "numLikes": 1,
    "url": "/api/v1/likes/1/"
  };  

  const [imgUrl, setImgUrl] = useState("");
  const [owner, setOwner] = useState("");
  const [comments, setComments] = useState([]);
  const [likes, setLikes] = useState(initialLikes);
  const [createdAt, setCreatedAt] = useState("");
  // const [nextPageUrl, setNextPageUrl] = useState(null); // State to store next page URL


  useEffect(() => {
    // Declare a boolean flag that we can use to cancel the API request.
    let ignoreStaleRequest = false;

    // Call REST API to get the post's information
    fetch(url, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        // If ignoreStaleRequest was set to true, we want to ignore the results of the
        // the request. Otherwise, update the state to trigger a new render.
        if (!ignoreStaleRequest) {
          setImgUrl(data.imgUrl);
          setOwner(data.owner);
          setComments(data.comments);
          setLikes(data.likes);

         
          const localTime = dayjs.utc(data.createdAt).local();
          // const formattedTimestamp = localTime.format("YYYY-MM-DD HH:mm:ss"); TODO: never used
          const humanReadableTimestamp = localTime.fromNow();
          setCreatedAt(humanReadableTimestamp);

          // setPosts((prevPosts) => [...prevPosts, ...data.results]);
          // setNextPageUrl(data.next); // Store the next page URL
        }
      })
      .catch((error) => console.log(error));

    return () => {
      // This is a cleanup function that runs whenever the Post component
      // unmounts or re-renders. If a Post is about to unmount or re-render, we
      // should avoid updating state.
      ignoreStaleRequest = true;
    };
  }, [url]);

  const toggleLike = () => {
    const postid = 1
    // Determine if the action is to create (like) or delete (unlike)
    const isLiked = likes.lognameLikesThis;
    const requestOptions = {
      method: isLiked ? 'DELETE' : 'POST',
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
      },
      body: isLiked ? JSON.stringify({ }): JSON.stringify({ postid: 1 }),
    };
  
    // may need to be postid=${encodeURIComponent(postid)}
    const likeurl = isLiked ? likes.url: `http://localhost:8000/api/v1/likes/?postid=${postid}`; 
    console.log(likeurl)
    console.log(requestOptions.method)
    fetch(likeurl, requestOptions)
      .then((response) => {
        console.log(response);
        if (!response.ok) {
          const contentType = response.headers.get('Content-Type');
          if (contentType && contentType.includes('application/json')) {
            // Parse response as JSON if the Content-Type is 'application/json'
            return response.json().then((data) => Promise.reject(data));
          }
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        if (response.ok) {
          // For DELETE requests with a 204 response, handle here without .json() parsing
          if (response.status === 204) {
            return {}; // Return an empty object which will be used in the follow-up .then()
          }
        }
        return response.json();
      })
      .then((data) => {
        setLikes(() => {
          if (!isLiked) {
            // Handle new like
            return {
              lognameLikesThis: true,
              numLikes: likes.numLikes + 1,
              url: data.url, // Assuming the backend returns the correct like URL
            };
          }
          // Handle unlike
          return {
            lognameLikesThis: false,
            numLikes: likes.numLikes - 1,
            url: '', // Clear the URL as it's an 'unlike' request
          };
        });
      })
      .catch((error) => {
        console.error('Error during toggle:', error);
        // Consider how to communicate this error to the user
      });
  };

  const handleDeleteComment = (commentid) => {

    let ignoreStaleRequest = false;

    console.log(commentid);
    const commentUrl = `/api/v1/comments/${commentid}/`;
    fetch(commentUrl, {
       credentials: "same-origin",
       method: "DELETE"
      })
    .then((response) => {
      if (!response.ok) throw Error(response.statusText);
      return response.json();
    })
    .then((data) => {
      // If ignoreStaleRequest was set to true, we want to ignore the results of the
      // the request. Otherwise, update the state to trigger a new render.
      if (!ignoreStaleRequest) {
        setImgUrl(data.imgUrl);
        setOwner(data.owner);
        setComments(data.comments);
        setLikes(data.likes);

       
        const localTime = dayjs.utc(data.createdAt).local();
        // const formattedTimestamp = localTime.format("YYYY-MM-DD HH:mm:ss");
        const humanReadableTimestamp = localTime.fromNow();
        setCreatedAt(humanReadableTimestamp);

        // Store the URL for the next set of posts
        // setNextPostUrl(data.next);

      }
    })
    .catch((error) => console.log(error));
    return () => {
      // This is a cleanup function that runs whenever the Post component
      // unmounts or re-renders. If a Post is about to unmount or re-render, we
      // should avoid updating state.
      ignoreStaleRequest = true;
    };

}

  
  // const handleNextPage = () => {
  //   if (nextPageUrl) {
  //     setUrl(nextPageUrl); // Fetch the next page
  //   }
  // };

  // Render post image and post owner

  //  
  return (
    <div className="post">
      <p>{owner}</p>
      <p>{createdAt}</p>
      <img src={imgUrl} alt="post_image" />

      < Likes likes = {likes} onToggleLike={toggleLike}/>
      < Comments comments={comments} handleDeleteComment={handleDeleteComment} />

     
    </div>
  );
}

Post.propTypes = {
  url: PropTypes.string.isRequired,
};

