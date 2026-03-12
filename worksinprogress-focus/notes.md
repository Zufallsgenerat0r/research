# Works in Progress Magazine - Research Notes

## Approach

### Data Collection (2026-03-12)
- Attempted direct scraping of worksinprogress.co — blocked by network proxy (403 host_not_allowed)
- Pivoted to systematic web search approach:
  - Searched for main site, archive page, author page
  - Searched each issue page individually (issue-10 through issue-21)
  - Cross-referenced Substack newsletter announcements for each issue
  - Searched for specific popular articles to confirm authorship
  - Used Muck Rack for recent article dates

### Challenges
- The website blocks programmatic access (proxy restrictions in this environment)
- Search engine snippets don't always include full article titles — some are described by topic rather than exact title
- Earlier issues (1-9) were harder to find complete listings for; relied on scattered mentions
- Some articles appeared in search results associated with different issue numbers than expected — the archive may have been reorganized or articles may have been reassigned to print issues vs. online issues

### What I Learned
- Works in Progress was founded in 2020 by Sam Bowman, Saloni Dattani, Nick Whitaker, and Ben Southwood
- Funded initially by Tyler Cowen's Emergent Ventures grant
- Now part of Stripe (the payments company)
- Magazine publishes quarterly-ish, now up to Issue 21+ (Issue 23 expected April 2026)
- Has grown significantly — earlier issues had ~3-5 articles, later issues have 7-10
- Very strong housing/urban planning focus (their most viral article is "The Housing Theory of Everything")
- Broad "progress studies" orientation: science, technology, economics, policy, health
- Mix of academics, journalists, think tank researchers, and independent writers

### Data Quality Notes
- Compiled ~116 article entries across 21 issues
- 72 unique authors identified
- 28 fine-grained topic tags, grouped into 11 broad categories
- Some duplication possible where articles from the web search appeared under different issue contexts
- Author bios sourced from the /our-authors/ page descriptions in search results

### Key Findings
1. **Samuel Hughes** is the most prolific author (8 articles), focused on housing, architecture, and aesthetics
2. **Samuel Watling** is second (6 articles), spanning housing, history, and policy
3. **Brian Potter** (Construction Physics) is third with 4 articles on construction/infrastructure
4. Economics & Policy dominates at ~27% of all topic tags
5. Science & Innovation is second at ~17%
6. Housing & Urban Planning is the third most common broad category
7. The magazine has grown from ~3 articles per issue in 2020 to 7-10 per issue in 2024-2025
8. Most authors are one-time contributors; only ~20 have written 2+ articles
9. Co-authored articles are relatively rare — most are solo pieces
10. The editorial team (Bowman, Dattani, Southwood, Hughes, Whitaker) also contributes articles
