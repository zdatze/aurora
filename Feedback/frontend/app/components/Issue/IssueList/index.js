import React from 'react';

import IssueTeaser from '../IssueTeaser';

const IssueList = ({issues, isStaff, current_user, onDrop}) => {
  // Build up the issues teasers.
  const issueTeasers = issues.map(issue => {
    let number_comments = 0;
    let upvotes = 0;

    if (issue['comments'] !== undefined) {
      number_comments = issue.comments;
    }

    if (issue['upvotes'] !== undefined) {
      upvotes = issue['upvotes'];
    }

    return (
      <li key={issue.id} className="issue-list__item">
        <IssueTeaser title={issue.title} upvotes={upvotes}
                     comments={number_comments} id={issue.id} type={issue.type}
                     lane={issue.lane.id} onDrop={onDrop}
                     preview={issue.preview !== undefined ? issue.preview : false}
                     canDrag={isStaff}
                     isAuthor={current_user == issue.author.id}
                     body={issue.body} archived={issue.archived} />
      </li>
    );
  });

  // Build up the empty message.
  const msg = (
    <li className="issue-list__empty">
      No issues here yet.
    </li>
  );

  return (
    <ul>
      { issues.length > 0 ? issueTeasers : msg }
    </ul>
  );
};

export default IssueList;