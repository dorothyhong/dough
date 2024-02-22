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
export default function Post({ url, postId }) {
  /* Display image and post owner of a single post */

  const initialLikes = {
    lognameLikesThis: false,
    numLikes: 1,
    url: "/api/v1/likes/1",
  };

  const [ownerImgUrl, setOwnerImgUrl] = useState("");
  const [imgUrl, setImgUrl] = useState("");
  const [owner, setOwner] = useState("");
  const [comments, setComments] = useState([]);
  const [likes, setLikes] = useState(initialLikes);
  const [createdAt, setCreatedAt] = useState("");
  const [postShowUrl, setPostShowUrl] = useState("");

  const [dataLoaded, setDataLoaded] = useState(false);

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
          setOwnerImgUrl(data.ownerImgUrl);
          setImgUrl(data.imgUrl);
          setOwner(data.owner);
          setComments(data.comments);
          setLikes(data.likes);
          setPostShowUrl(data.postShowUrl);

          const localTime = dayjs.utc(data.createdAt).local();
          const humanReadableTimestamp = localTime.fromNow();
          setCreatedAt(humanReadableTimestamp);

          setDataLoaded(true);
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
    // Determine if the action is to create (like) or delete (unlike)
    const isLiked = likes.lognameLikesThis;

    console.log("Initial lognameLikesThis: ", likes.lognameLikesThis);
    console.log("Toggling like for post ID:", postId);
    console.log("Previous like status:", isLiked);

    const requestOptions = {
      method: isLiked ? "DELETE" : "POST",
      credentials: "same-origin",
      headers: {
        "Content-Type": "application/json",
      },
      // body removed for DELETE request
      body: isLiked ? undefined : JSON.stringify({ postid: postId }),
    };

    // may need to be postid=${encodeURIComponent(postid)}
    const likeurl = isLiked ? likes.url : `/api/v1/likes/?postid=${postId}`;

    console.log("Sending request to:", likeurl);
    console.log("Request method:", requestOptions.method);

    fetch(likeurl, requestOptions)
      .then((response) => {
        console.log("Response status:", response.status);
        console.log(response);

        if (!response.ok) {
          const contentType = response.headers.get("Content-Type");
          if (contentType && contentType.includes("application/json")) {
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
        console.log("Response data:", data);

        if (!isLiked) {
          setLikes({
            lognameLikesThis: true,
            numLikes: likes.numLikes + 1,
            url: data.url,
          });
        } else {
          setLikes({
            lognameLikesThis: false,
            numLikes: likes.numLikes - 1,
            url: null,
          });
        }
      })
      .catch((error) => {
        console.error("Error during toggle:", error);
        // Consider how to communicate this error to the user
      });
  };

  const handleDoubleClick = () => {
    if (!likes.lognameLikesThis) {
      console.log("here");
      toggleLike(); // like the image if it's not liked already
    }
    // Do nothing if the image is already liked
  };

  const handleCreateComment = (text, onSuccess) => {
    const commentUrl = `/api/v1/comments/?postid=${postId}`;
    fetch(commentUrl, {
      credentials: "same-origin",
      method: "POST",
      body: JSON.stringify({ text }),
      headers: {
        "Content-Type": "application/json", // Missing 'Content-Type' header
      },
    })
      .then((response) => {
        console.log("COMMENTS POST");
        console.log("Response status:", response.status);
        console.log(response);

        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        console.log("Response data:", data);

        setComments([...comments, data]);
        console.log(comments);
        if (onSuccess) {
          onSuccess(data);
        }
      })
      .catch((error) => console.log(error));
    return () => {};
  };

  const handleDeleteComment = (commentid) => {
    console.log(commentid);
    const commentUrl = `/api/v1/comments/${commentid}`;
    fetch(commentUrl, {
      credentials: "same-origin",
      method: "DELETE",
    })
      .then((response) => {
        console.log("COMMENTS POST");
        console.log("Response status:", response.status);
        console.log(response);

        if (!response.ok) throw Error(response.statusText);
        setComments((prevComments) =>
          prevComments.filter((comment) => comment.commentid !== commentid),
        );
      })
      .catch((error) => console.log(error));
    return () => {
      // This is a cleanup function that runs whenever the Post component
      // unmounts or re-renders. If a Post is about to unmount or re-render, we
      // should avoid updating state.
      // ignoreStaleRequest = true;
    };
  };

  // Render post image and post owner
  return (
    <div className="post">
      <img
        src={ownerImgUrl}
        alt="profile_image"
        // Optional: indicates the image is interactive
      />
      <p>{owner}</p>
      <a href={postShowUrl}>{createdAt}</a>
      <img
        src={imgUrl}
        alt="post_image"
        onDoubleClick={handleDoubleClick}
        style={{ cursor: "pointer" }}
      />
      {dataLoaded && <Likes likes={likes} onToggleLike={toggleLike} />}
      <Comments
        comments={comments}
        handleDeleteComment={handleDeleteComment}
        handleCreateComment={handleCreateComment}
      />
    </div>
  );
}

Post.propTypes = {
  url: PropTypes.string.isRequired,
  postId: PropTypes.number.isRequired,
};
