import React from "react";
import PropTypes from "prop-types";

export default function Likes({ likes, onToggleLike }) {
    const buttonText = likes.lognameLikesThis ? 'Unlike' : 'Like';
    return (
        <div>
            <button type="button" data-testid="like-unlike-button" onClick={onToggleLike}>
                {buttonText}
            </button>
            {likes.numLikes}
            {likes.numLikes > 1 ? "likes" : "like"}
        </div>
    );
}

Likes.propTypes = {
    likes: PropTypes.shape({
      lognameLikesThis: PropTypes.bool.isRequired,
      numLikes: PropTypes.number.isRequired,
      url: PropTypes.oneOfType([PropTypes.string, PropTypes.oneOf([null])]).isRequired,
    }).isRequired,
    onToggleLike: PropTypes.func.isRequired, 
};
