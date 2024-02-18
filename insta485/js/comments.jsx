import React from "react";
import PropTypes from "prop-types";

// condition ? exprIfTrue : exprIfFalse

export default function Comments({ comments, handleDeleteComment }) {

    
    const renderedCommentList = comments.map((comment) => (
        
            <div key={comment.commentid} >
                <a href={`/users/${ comment.owner }/`}>{comment.owner}</a>
                <div>{comment.text}</div>
                <div>{comment.lognameOwnsThis 
                ? <button type="button" onClick={() => handleDeleteComment(comment.commentid)}>Delete</button> : " " }
                </div>
            </div>
            
    ));
    

    return (
        <div>{renderedCommentList}</div>
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
};
  