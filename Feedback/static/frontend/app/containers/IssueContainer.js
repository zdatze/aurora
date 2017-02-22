import {connect} from 'react-redux'
import {IssueDetail} from '../components/Issue'
import {changeIssue} from '../actions/issueActions';

const mapStateToProps = (state, ownProps) => {
  const issue = state.issues.filter(issue => {
    return issue.id == ownProps.params.id
  })[0];

  return {
    issue: issue
  };

};

const mapDispatchToProps = (dispatch) => {
  return {
    update: (id, type, title, body) => {
      dispatch(changeIssue({type: type, title: title, body: body}, id))
    }
  };
};

const IssueContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(IssueDetail);

export default IssueContainer;