# CodeRabbit thread operations — gh-api recipes (Stage 2.5)

When responding to existing CodeRabbit review threads — replying, dismissing with reasoning, or marking resolved — the gh-api shape matters. Pattern from [openhuman `.claude/commands/ship-and-babysit.md` Phase 4](https://github.com/tinyhumansai/openhuman/blob/main/.claude/commands/ship-and-babysit.md):

**Reply inside an existing thread** (so the reply attaches to the same conversation, not a brand-new review):
```bash
gh api repos/<owner>/<repo>/pulls/comments/<comment_id>/replies \
  -X POST \
  -f body='**Dismissed:** <reason>'
```
`<comment_id>` is the top-level review-comment id from `gh api repos/<owner>/<repo>/pulls/<PR#>/comments`. **Do NOT use `POST /pulls/<PR#>/reviews`** for replies — that creates a *new* review thread, not a reply, and orphans the original conversation.

**Resolve a thread after fixing or dismissing:**
```bash
gh api graphql -f query='mutation($id:ID!){resolveReviewThread(input:{threadId:$id}){thread{isResolved}}}' -f id=<threadId>
```

**List thread ids — paginated, cap of 100 per page.** `reviewThreads(first:100)` silently truncates past 100; threads on page 2+ slip past any "all resolved?" exit check. Loop on `pageInfo.hasNextPage` / `endCursor`:
```bash
gh api graphql -f query='query($owner:String!,$repo:String!,$num:Int!,$cursor:String){
  repository(owner:$owner,name:$repo){
    pullRequest(number:$num){
      reviewThreads(first:100, after:$cursor){
        pageInfo{hasNextPage endCursor}
        nodes{id isResolved comments(first:1){nodes{author{login} body}}}
      }
    }
  }
}' -F owner=<owner> -F repo=<repo> -F num=<PR#> -F cursor=
```
Feed `endCursor` back as `$cursor` until `hasNextPage: false`.
