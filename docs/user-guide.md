# WorkMetrics User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Dashboard Overview](#dashboard-overview)
4. [Four Keys Metrics](#four-keys-metrics)
5. [Team Activity Analysis](#team-activity-analysis)
6. [Cycle Time Analysis](#cycle-time-analysis)
7. [Project Management](#project-management)
8. [Tips & Best Practices](#tips--best-practices)
9. [Troubleshooting](#troubleshooting)

---

## Introduction

WorkMetrics is a comprehensive GitLab metrics dashboard that helps teams track and improve their software delivery performance. It provides three main analytical views:

- **Four Keys Metrics**: DORA DevOps performance indicators
- **Team Activity**: Individual contributor productivity insights
- **Cycle Time Analysis**: Process bottleneck identification

### Who Should Use WorkMetrics?

- **Engineering Managers**: Track team performance and identify areas for improvement
- **DevOps Engineers**: Monitor deployment frequency and reliability
- **Process Specialists**: Analyze cycle time and optimize workflows
- **Team Leads**: Understand individual contributions and review load distribution

---

## Getting Started

### Prerequisites

- GitLab account with a project
- GitLab Personal Access Token with `api` and `read_repository` scopes
- WorkMetrics application access

### Initial Setup

1. **Configure GitLab Access**
   - Go to GitLab → User Settings → Access Tokens
   - Create a new token with `api` and `read_repository` scopes
   - Copy the token (you won't be able to see it again)
   - Add the token to WorkMetrics configuration

2. **Add Your First Project**
   - Navigate to "Project Settings" in WorkMetrics
   - Click "Add New Project"
   - Enter your GitLab project ID
   - Click "Save"

3. **Initial Data Sync**
   - Click "Refresh Data" to sync project data from GitLab
   - Wait for the initial sync to complete (may take a few minutes)
   - Data will automatically refresh daily

---

## Dashboard Overview

The main dashboard provides three tabs for different analytical views:

### Navigation

- **Tab Switching**: Click on tabs or use keyboard shortcuts
  - `Arrow Left/Right`: Navigate between tabs
  - `Home`: Jump to first tab
  - `End`: Jump to last tab

- **Project Selection**: Use the dropdown at the top to switch between projects

- **Time Range**: Each tab has a time range selector for filtering data

### Keyboard Shortcuts

- `←` / `→`: Previous/Next tab
- `Home`: First tab (Four Keys)
- `End`: Last tab (Cycle Time)
- `Tab`: Navigate through interactive elements

---

## Four Keys Metrics

The Four Keys tab displays DORA (DevOps Research and Assessment) metrics that measure software delivery performance.

### Metrics Explained

#### 1. Deployment Frequency

**What it measures**: How often you successfully release to production

**Interpretation**:
- **Elite**: Multiple deploys per day
- **High**: Once per day to once per week
- **Medium**: Once per week to once per month
- **Low**: Less than once per month

**How to improve**:
- Automate deployment processes
- Implement CI/CD pipelines
- Break down large releases into smaller chunks
- Reduce manual approval steps

#### 2. Lead Time for Changes

**What it measures**: Time from code commit to code running in production

**Interpretation**:
- **Elite**: Less than 1 hour
- **High**: 1 day to 1 week
- **Medium**: 1 week to 1 month
- **Low**: More than 1 month

**How to improve**:
- Streamline code review process
- Automate testing
- Reduce build times
- Parallelize deployment stages

#### 3. Change Failure Rate

**What it measures**: Percentage of deployments that cause failures

**Interpretation**:
- **Elite**: 0-15%
- **High**: 16-30%
- **Medium**: 31-45%
- **Low**: More than 45%

**How to improve**:
- Increase test coverage
- Implement feature flags
- Use canary deployments
- Improve staging environment accuracy

#### 4. Time to Restore Service

**What it measures**: How long it takes to recover from a production failure

**Interpretation**:
- **Elite**: Less than 1 hour
- **High**: Less than 1 day
- **Medium**: 1 day to 1 week
- **Low**: More than 1 week

**How to improve**:
- Implement monitoring and alerting
- Practice incident response
- Automate rollback procedures
- Maintain good documentation

### Using the Four Keys Tab

1. **Select Time Range**: Choose the period you want to analyze
2. **View Metrics**: Each metric shows current value and trend
3. **Compare Periods**: Use historical data to track improvements
4. **Export Data**: Click "Export" to download metrics for reporting

---

## Team Activity Analysis

The Team Activity tab helps you understand individual contributions and identify workload imbalances.

### Metrics Displayed

#### Commit Activity

- **Total Commits**: Number of commits per team member
- **Commit Patterns**: When team members are most active
- **Lines Changed**: Code additions and deletions

#### Merge Request Activity

- **MRs Created**: Number of merge requests opened
- **MRs Merged**: Successfully merged requests
- **Average MR Size**: Typical size of changes

#### Review Load

- **Reviews Given**: Number of code reviews performed
- **Review Distribution**: How review work is shared across the team
- **Response Time**: How quickly reviews are completed

### Interpreting the Data

**Balanced Team**:
- Review load distributed evenly (±20%)
- Similar commit frequency across members
- No bottlenecks in code review

**Warning Signs**:
- One person doing 50%+ of reviews (reviewer bottleneck)
- Large variance in commit counts (potential capacity issues)
- High MR counts with low merge rates (review delays)

### Action Items

**If review load is imbalanced**:
- Rotate code reviewers
- Set review quotas
- Use automated code review tools
- Provide review training

**If commit patterns are concerning**:
- Check for blockers or dependencies
- Review task assignments
- Consider pairing or mentoring
- Adjust capacity planning

---

## Cycle Time Analysis

The Cycle Time tab breaks down development process into stages to identify bottlenecks.

### Stages Explained

#### 1. Coding (💻)

**What it measures**: Time from first commit to MR creation

**Typical duration**: 0.5-2 days

**Bottleneck indicators**:
- Mean > 5 days: Tasks may be too large
- High variance (p90 >> median): Inconsistent task sizing

**How to improve**:
- Break down features into smaller tasks
- Encourage more frequent MR creation
- Use feature branches effectively

#### 2. Review (👀)

**What it measures**: Time from MR creation to merge

**Typical duration**: 0.5-3 days

**Bottleneck indicators**:
- Mean > 5 days: Review capacity issue
- High variance: Priority confusion or availability problems

**How to improve**:
- Assign reviewers explicitly
- Set SLAs for code review
- Keep MRs small (< 400 lines)
- Use draft MRs for early feedback

#### 3. Deployment (🚀)

**What it measures**: Time from merge to production deployment

**Typical duration**: 0.1-1 day

**Bottleneck indicators**:
- Mean > 2 days: Deployment process issues
- High variance: Manual deployment steps

**How to improve**:
- Automate deployment pipeline
- Deploy more frequently
- Reduce manual approvals
- Implement continuous deployment

### Using the Cycle Time Tab

1. **View Stage Breakdown**
   - See which stage takes the most time
   - Identify the dominant bottleneck

2. **Check Percentiles**
   - **Median (p50)**: Typical cycle time
   - **75th percentile (p75)**: Upper normal range
   - **90th percentile (p90)**: Outlier threshold

3. **Analyze Distribution**
   - Review top 20 slowest MRs
   - Look for patterns (specific types, sizes, or authors)
   - Investigate outliers

4. **Track Improvements**
   - Compare metrics across time periods
   - Verify process changes are working
   - Celebrate improvements with the team

### Interpreting Insights

**Coding-dominant (>50%)**:
```
💡 Tasks may be too large. Consider:
- Breaking features into smaller chunks
- More frequent commits
- Incremental development
```

**Review-dominant (>50%)**:
```
💡 Review bottleneck detected. Consider:
- Increasing reviewer availability
- Smaller MRs
- Clear review guidelines
- Automated checks
```

**Deployment-dominant (>30%)**:
```
💡 Deployment delays detected. Consider:
- Automating CI/CD pipeline
- Removing manual steps
- More frequent deployments
- Parallel deployment stages
```

---

## Project Management

### Adding a Project

1. Navigate to "Project Settings"
2. Click "Add New Project"
3. Enter GitLab Project ID (found in project settings)
4. Optionally configure:
   - Display name
   - Refresh frequency
   - GitLab instance URL (if self-hosted)
5. Click "Save"

### Refreshing Data

**Manual Refresh**:
1. Select project in dashboard
2. Click "Refresh Data" button
3. Wait for sync to complete

**Automatic Refresh**:
- Data refreshes daily at 2:00 AM (default)
- Configure schedule in settings
- Respects GitLab API rate limits

### Managing Multiple Projects

- Switch between projects using the dropdown
- Compare metrics across projects
- Set favorites for quick access
- Archive inactive projects

---

## Tips & Best Practices

### Getting Accurate Metrics

1. **Tag Deployments Properly**
   - Use consistent deployment tags in GitLab
   - Tag production deployments separately from staging
   - Include timestamp in deployment metadata

2. **Link Issues to MRs**
   - Reference issues in MR descriptions
   - Use GitLab's issue closing keywords
   - Track feature work end-to-end

3. **Maintain Clean Commit History**
   - Write meaningful commit messages
   - Link commits to issues/MRs
   - Use conventional commit format

### Interpreting Trends

**Look for patterns over time**:
- Metrics should improve gradually
- Sudden changes may indicate process changes or issues
- Seasonal patterns (holidays, sprints) are normal

**Compare with industry benchmarks**:
- Use DORA benchmarks as reference
- Don't obsess over absolute numbers
- Focus on continuous improvement

**Avoid common pitfalls**:
- Don't compare teams directly (different contexts)
- Don't use metrics for individual performance reviews
- Don't optimize one metric at the expense of others

### Team Communication

**Share insights regularly**:
- Review metrics in retrospectives
- Celebrate improvements
- Discuss bottlenecks openly
- Involve team in process improvements

**Set realistic goals**:
- Incremental improvements over time
- Focus on one or two metrics at a time
- Experiment and measure results

---

## Troubleshooting

### Data Not Loading

**Symptoms**: Dashboard shows "No data" or loading spinner indefinitely

**Solutions**:
1. Check GitLab token is valid and has correct scopes
2. Verify project ID is correct
3. Check GitLab API is accessible
4. Review backend logs for errors
5. Manually trigger data refresh

### Metrics Seem Incorrect

**Symptoms**: Numbers don't match expectations or are unrealistic

**Solutions**:
1. Verify deployment tagging is consistent
2. Check time zone settings
3. Ensure all team members are tracked
4. Review data refresh logs
5. Validate GitLab webhooks (if configured)

### Slow Performance

**Symptoms**: Dashboard loads slowly or times out

**Solutions**:
1. Reduce time range for analysis
2. Check database performance
3. Review backend resource usage
4. Consider data archiving for old projects
5. Optimize GitLab API calls (check rate limits)

### Missing Team Members

**Symptoms**: Some contributors don't appear in Team Activity

**Solutions**:
1. Verify team members have GitLab accounts
2. Check project member permissions
3. Ensure commits are attributed correctly
4. Refresh project data
5. Review email matching configuration

### Common Error Messages

**"GitLab API rate limit exceeded"**
- Wait for rate limit reset (usually 1 hour)
- Reduce refresh frequency
- Contact GitLab admin to increase limits

**"Failed to connect to GitLab"**
- Check network connectivity
- Verify GitLab URL is correct
- Check firewall/proxy settings
- Ensure SSL certificates are valid

**"Project not found"**
- Verify project ID
- Check token has access to project
- Ensure project is not archived
- Try re-adding the project

---

## Keyboard Accessibility

WorkMetrics is fully keyboard-accessible:

- **Tab**: Move through interactive elements
- **Enter/Space**: Activate buttons
- **Arrow Keys**: Navigate tabs
- **Escape**: Close modals/dropdowns
- **Home/End**: Jump to first/last tab

Screen reader support is included for visually impaired users.

---

## Support & Feedback

### Getting Help

- **Documentation**: https://github.com/HackathonTeamC/WorkMetrics
- **Issues**: https://github.com/HackathonTeamC/WorkMetrics/issues
- **Email**: support@workmetrics.example.com

### Providing Feedback

We welcome your feedback! Please:
- Report bugs via GitHub Issues
- Suggest features via Discussions
- Share success stories with the community
- Contribute to documentation improvements

---

## Changelog

### Version 0.1.0 (Current)

**Features**:
- Four Keys Metrics dashboard
- Team Activity analysis
- Cycle Time analysis with stage breakdown
- GitLab integration
- Automated data refresh
- Keyboard navigation
- Error boundary for stability

**Coming Soon**:
- Custom metric definitions
- Slack/email notifications
- Advanced filtering and segmentation
- Predictive analytics
- Multi-project comparisons
- Export and reporting tools

---

## Glossary

- **DORA**: DevOps Research and Assessment
- **MR**: Merge Request (GitLab's term for Pull Request)
- **CI/CD**: Continuous Integration/Continuous Deployment
- **Lead Time**: Time from code commit to production
- **Cycle Time**: Time from work start to completion
- **Deployment Frequency**: How often code is deployed
- **MTTR**: Mean Time To Recovery
- **CFR**: Change Failure Rate

---

**Last Updated**: 2024-11-27  
**Version**: 0.1.0
