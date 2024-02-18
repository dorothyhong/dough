import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import Comments from "./comments"
import Likes from "./likes"

import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import utc from "dayjs/plugin/utc";

dayjs.extend(relativeTime);
dayjs.extend(utc);

// The parameter of this function is an object with a string called url inside it.
// url is a prop forhfhrt the Post component.
export default function Post({ url }) {
  /* Display image and post owner of a single post */

  const initialLikes = {
    "lognameLikesThis": true,
    "numLikes": 1,
    "url": "/api/v1/likes/6/"
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
          const formattedTimestamp = localTime.format("YYYY-MM-DD HH:mm:ss");
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
    const requestOptions = {
      method: likes.lognameLikesThis ? 'DELETE' : 'POST',
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
      },
    };
    console.log(likes.url);
    fetch(likes.url, requestOptions)
      .then((response) => {
        if (!response.ok) {
          const contentType = response.headers.get('Content-Type');
          if (contentType && contentType.includes('application/json')) {
            // Parse response as JSON if the Content-Type is 'application/json'
            return response.json().then((data) => Promise.reject(data));
          } else {
            // If response is not JSON, it could be text or HTML
            return response.text().then((text) => Promise.reject(text));
          }
        }
        return response.json();
      })
      .then((data) => {
        // Existing toggle logic...
      })
      .catch((error) => {
        console.error('Error during toggle:', error);
        // You might want to show an error message to the user here
      });
  };

  const handleDeleteComment = (commentid) => {
    url = `/api/v1/comments/${commentid}/`
    fetch(url, {
       credentials: "same-origin" 
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
        const formattedTimestamp = localTime.format("YYYY-MM-DD HH:mm:ss");
        const humanReadableTimestamp = localTime.fromNow();
        setCreatedAt(humanReadableTimestamp);

        // Store the URL for the next set of posts
        // setNextPostUrl(data.next);

      }
    })
    .catch((error) => console.log(error));

}

  
  // const handleNextPage = () => {
  //   if (nextPageUrl) {
  //     setUrl(nextPageUrl); // Fetch the next page
  //   }
  // };

  // Render post image and post owner
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

