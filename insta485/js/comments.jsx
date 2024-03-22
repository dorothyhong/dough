import React, { useState } from "react";
import PropTypes from "prop-types";
// import "../css/style.css";

export default function Comments({
  comments,
  handleDeleteComment,
  handleCreateComment,
}) {
  const [text, setText] = useState("");

  const renderedCommentList = comments.map((comment) => (
    <div key={comment.commentid}>
      <a href={`/users/${comment.owner}/`}>{comment.owner}</a>
      <span data-testid="comment-text">{comment.text}</span>
      <div>
        {comment.lognameOwnsThis ? (
          <button
            data-testid="delete-comment-button"
            type="button"
            onClick={() => handleDeleteComment(comment.commentid)}
          >
            Delete
          </button>
        ) : (
          " "
        )}
      </div>
    </div>
  ));

  const handleTextChange = (event) => {
    setText(event.target.value);
  };

  return (
    <div>
      <div>{renderedCommentList}</div>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleCreateComment(text, () => {
            setText("");
          });
        }}
        data-testid="comment-form"
      >
        <input type="text" onChange={handleTextChange} value={text} />
      </form>
    </div>
  );
}

Comments.propTypes = {
  comments: PropTypes.arrayOf(
    PropTypes.shape({
      commentid: PropTypes.number.isRequired,
      lognameOwnsThis: PropTypes.bool.isRequired,
      owner: PropTypes.string.isRequired,
      ownerShowUrl: PropTypes.string.isRequired,
      text: PropTypes.string.isRequired,
      url: PropTypes.string.isRequired,
    }),
  ).isRequired,
  handleDeleteComment: PropTypes.func.isRequired,
  handleCreateComment: PropTypes.func.isRequired,
};
