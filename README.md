# GitHub Topic Recommender — Find the Best GitHub Topics for Your Repository

![Python 3.13+](https://img.shields.io/badge/python-3.13%2B-blue)
![Status: MVP](https://img.shields.io/badge/status-MVP-orange)
![No LLM required](https://img.shields.io/badge/AI-not%20required-lightgrey)

**GitHub Topic Recommender is a free, open-source CLI that analyzes your project and recommends relevant, popular GitHub repository topics (repo tags) to improve discoverability on GitHub.**

It answers a common question — *"which GitHub topics should I add to my repository?"* — with evidence instead of guesswork: it finds comparable repositories on GitHub, measures which topics they actually use, and ranks candidates by niche prevalence, popularity, activity, specificity, and relevance to your project.

Use it to choose accurate repository topics for developer tools, open-source libraries, frameworks, CLIs, applications, datasets, and emerging fields such as DevSecOps, AI security, MLSecOps, platform engineering, and agentic engineering.

> **What are GitHub topics?** Topics are the public labels (tags) attached to a GitHub repository. They classify the project, power GitHub's `topic:` search qualifier and topic pages, and help users discover related projects and technical communities. Choosing established, relevant topics is one of the highest-leverage ways to make a repository easier to find on GitHub.

## Quick Start

```bash
# Install with Poetry (Python 3.13+, from a clone of this repository)
poetry install

# Recommend topics for an existing GitHub repository
poetry run github-topic-recommender analyze OWNER/REPOSITORY

# Recommend topics from a plain-text project description
poetry run github-topic-recommender recommend --description "An open-source DevSecOps dependency scanner"

# See which topics a niche actually uses
poetry run github-topic-recommender explore "AI security"
```


## Why GitHub Topic Recommender?

Choosing repository topics manually can be difficult:

- Which topic names are already established on GitHub?
- Which topics are commonly used by comparable projects?
- Is a topic relevant or merely popular?
- Which terms best represent a new or emerging niche?
- Are important topic categories missing from the repository?
- Which combination of broad and specific topics should be used?

GitHub Topic Recommender analyzes repository metadata and comparable projects to produce a focused set of evidence-based topic recommendations.

## Features

- **Project analysis** — Analyze a repository description, README, metadata, and technology stack.
- **Niche discovery** — Identify topics associated with a field, market, or technical category.
- **Comparable repositories** — Find relevant GitHub projects and inspect their topic usage.
- **Topic popularity** — Measure how frequently topics appear across comparable repositories.
- **Semantic relevance** — Rank topics by how closely they match the project’s purpose.
- **Topic co-occurrence** — Discover topics that are frequently assigned together.
- **Specificity analysis** — Distinguish precise topics from broad or generic terms.
- **Activity signals** — Prioritize topics supported by active repositories.
- **Topic normalization** — Identify aliases, spelling variants, and near-duplicate topics.
- **Explainable recommendations** — Show why each topic was recommended.
- **Discoverability report** — Identify missing, redundant, or weak repository topics.

## Example

> Illustrative example. Actual output depends on the live GitHub sample at the time of analysis and always includes the evidence behind each topic.

### Input

```text
An open-source CLI that scans CI/CD pipelines for secrets,
vulnerable dependencies, and software supply-chain risks.
```

### Recommended topics

```text
devsecops
application-security
supply-chain-security
secret-scanning
dependency-scanning
software-composition-analysis
sbom
ci-cd
security-tools
command-line-tool
```

### Example explanation

| Topic | Role | Why it fits |
|---|---|---|
| `devsecops` | Primary niche | Directly describes security integrated into development and delivery workflows |
| `application-security` | Category | Connects the project to the broader AppSec ecosystem |
| `supply-chain-security` | Problem | Represents one of the project’s primary security concerns |
| `secret-scanning` | Capability | Describes a specific feature supported by the tool |
| `dependency-scanning` | Capability | Matches the project’s dependency analysis functionality |
| `sbom` | Standard/artifact | Connects the project to software bill-of-materials tooling |
| `command-line-tool` | Project type | Helps users discover CLI-based developer tools |

## How Does GitHub Topic Recommender Work?

GitHub Topic Recommender uses a multi-stage, fully deterministic analysis pipeline — no LLM or AI model is involved ([details](docs/recommend-command.md)).

### 1. Analyze the project

The tool examines available project information, including:

- Repository name and description
- README content
- Programming languages
- Frameworks and integrations
- Project type
- Intended audience
- Problems addressed
- Existing repository topics

### 2. Identify the project niche

The supplied content is converted into concepts and search queries representing the project’s:

- Primary field
- Technical category
- Capabilities
- Ecosystem
- Intended users
- Related technologies

### 3. Find comparable repositories

GitHub search and repository metadata are used to identify relevant projects through:

- Exact topic matches
- Repository descriptions
- README terminology
- Related concepts
- Semantic similarity
- Technology and language filters

### 4. Analyze topic usage

Topics from comparable repositories are aggregated and evaluated using signals such as:

- Niche prevalence
- Global popularity
- Topic specificity
- Repository quality
- Recent activity
- Topic co-occurrence
- Semantic relevance
- Niche lift

### 5. Generate recommendations

Candidate topics are ranked, filtered, and grouped into practical categories:

- Primary niche
- Project type
- Problems addressed
- Features and techniques
- Technologies and ecosystems
- Intended audience

## How Are Topics Ranked?

Raw popularity alone does not produce useful recommendations. Popular topics can be too broad, while highly relevant niche topics may appear less frequently.

GitHub Topic Recommender balances several signals:

```text
topic score =
    niche prevalence
  + semantic relevance
  + repository quality
  + topic specificity
  + co-occurrence strength
  + recent activity
  + topic maturity
  - genericity penalty
  - redundancy penalty
  - relevance penalty
```

The exact scoring weights may vary by analysis mode and available data.

### Niche prevalence

The percentage of comparable repositories using a topic:

```text
repositories in the niche using the topic
─────────────────────────────────────────
all analyzed repositories in the niche
```

### Niche lift

Lift measures whether a topic is disproportionately associated with the analyzed niche:

```text
P(topic | niche)
────────────────
P(topic)
```

For example, `python` may be popular within an AI-security sample but also common across GitHub. A topic such as `prompt-injection` may have lower overall usage but much stronger relevance and niche lift.

## Recommendation Strategies

The tool can support different recommendation strategies.

### Balanced

Combines established, specific, and project-level topics.

Best for most repositories.

### Conservative

Prioritizes mature topics with strong evidence and broad adoption.

Best for established products and libraries.

### Niche-focused

Prioritizes specialized topics with high relevance and niche lift.

Best for projects targeting a specific technical community.

### Emerging

Includes relevant topics that are growing but not yet widely established.

Best for new fields and rapidly evolving terminology.

## Use Cases

### New open-source projects

Find established GitHub topic names before publishing a new repository.

### Existing repositories

Audit current topics and identify relevant topics that may be missing.

### Developer tools

Position a CLI, library, API, framework, or GitHub application within the appropriate technical communities.

### Emerging niches

Map new terminology to established GitHub topics when the niche does not yet have a stable taxonomy.

### Competitive research

Analyze which topics are used by comparable repositories and how those projects position themselves.

### Repository portfolios

Apply a consistent topic strategy across repositories owned by a developer or organization.

## Example Niches

GitHub Topic Recommender can be used to investigate fields such as:

- DevSecOps
- AI security
- LLM security
- Application security
- Software supply-chain security
- Cloud-native development
- Platform engineering
- Developer experience
- Agentic engineering
- AI coding agents
- Machine learning operations
- Data engineering
- Privacy engineering
- Open-source intelligence

## Output

A recommendation report can include:

```json
{
  "project": {
    "name": "example-security-scanner",
    "type": "command-line tool",
    "primary_niche": "DevSecOps"
  },
  "sample": {
    "repositories_analyzed": 250,
    "active_repositories": 184
  },
  "recommendations": [
    {
      "topic": "devsecops",
      "score": 0.94,
      "role": "primary-niche",
      "niche_prevalence": 0.42,
      "lift": 18.6,
      "reason": "Directly represents the project's primary field"
    },
    {
      "topic": "secret-scanning",
      "score": 0.89,
      "role": "capability",
      "niche_prevalence": 0.27,
      "lift": 24.3,
      "reason": "Describes a core security-scanning capability"
    }
  ]
}
```

## Installation

Requires Python 3.13+. For a full walkthrough (including how to create a GitHub token), see [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md).

Install with [Poetry](https://python-poetry.org/) from a clone of this repository:

```bash
poetry install

# Or, including dev dependencies (pytest)
poetry install --with dev
```

Then run the CLI through Poetry's environment:

```bash
poetry run github-topic-recommender --help
```

To drop the `poetry run` prefix, activate the environment with `eval $(poetry env activate)`.

Set a GitHub token to raise API rate limits (optional but recommended).
The CLI reads `GITHUB_TOKEN` from the environment, loading it from a
`.env` file in the project root automatically:

```bash
cp .env.example .env
# then edit .env and set GITHUB_TOKEN=ghp_...
```

## Usage

### Analyze a GitHub repository

```bash
github-topic-recommender analyze OWNER/REPOSITORY
```

### Analyze a local project

```bash
github-topic-recommender recommend \
  --description "An open-source DevSecOps dependency scanner"
```

### Explore topics for a niche

```bash
github-topic-recommender explore "DevSecOps"
```

### Return machine-readable output

```bash
github-topic-recommender analyze OWNER/REPOSITORY --format json
```

Markdown reports are also supported with `--format markdown`.

### Limit the number of recommendations

```bash
github-topic-recommender analyze OWNER/REPOSITORY --limit 12
```

### Control the sample size

```bash
github-topic-recommender analyze OWNER/REPOSITORY --max-repos 200
```

See [mvp-implementation.md](mvp-implementation.md) for the MVP scope and architecture.

## Topic Selection Principles

Recommendations should follow several principles.

### Relevance before popularity

A popular topic should not be recommended unless the project genuinely supports it.

### Established names before invented names

Existing topic names usually offer more discoverability than newly invented variations.

### Specific and broad topics should coexist

A useful topic set typically combines:

- One or two broad categories
- One or more primary niche topics
- Specific capabilities or problems
- Relevant ecosystems or technologies
- The project or distribution type

### Avoid topic stuffing

Adding unrelated topics may attract the wrong audience and weaken the repository’s positioning. Recommendations should accurately represent the project.

### Avoid redundant variants

Closely related variants should be evaluated rather than assigned automatically. Examples include:

```text
appsec
application-security

llm-security
large-language-model-security

dev-tool
developer-tool
developer-tools
```

The tool should recommend the variant with the strongest combination of relevance, adoption, and established usage.

## GitHub Discoverability and SEO

Repository topics can directly support discovery within GitHub by helping users:

- Browse repositories associated with a subject
- Search with the `topic:` qualifier
- Find related projects and technical communities
- Understand a repository’s purpose at a glance

External search-engine benefits should be treated as secondary. Topics are public classification signals, but they are not a guaranteed Google or Bing ranking factor.

For better overall repository discoverability, combine accurate topics with:

- A clear repository name
- A concise repository description
- A descriptive README title
- A strong opening paragraph
- Consistent technical terminology
- Useful documentation and examples
- Active releases and maintenance
- Relevant links and community engagement

GitHub Topic Recommender optimizes **truthful topic selection**, not keyword stuffing or guaranteed search rankings.

### Suggested metadata for this repository

Practicing what it preaches, this repository should use a description and topics like:

```text
Description: CLI that recommends relevant, popular GitHub topics for your
repository based on evidence from comparable projects.

Topics: github-topics, discoverability, github-seo, seo, developer-tools,
cli, github-api, repository-management, open-source, devrel
```

## Data Sources

Depending on the implementation, analysis may use:

- GitHub REST API
- GitHub GraphQL API
- GitHub repository search
- Public repository metadata
- Repository topics
- README content
- Programming-language metadata
- Stars, forks, and activity signals
- Topic co-occurrence data

Users are responsible for complying with applicable GitHub API terms, rate limits, and acceptable-use requirements.

## Frequently Asked Questions

### How many topics can a GitHub repository have?

A GitHub repository can have up to 20 topics. In practice, a focused set of 5–12 accurate topics — mixing one or two broad categories, the primary niche, specific capabilities, key technologies, and the project type — usually serves discoverability better than using all 20.

### How do I add topics to a GitHub repository?

On the repository page, click the gear icon next to **About**, type topics into the **Topics** field, and save. From the command line: `gh repo edit OWNER/REPO --add-topic devsecops --add-topic cli`.

### Do GitHub topics improve SEO?

Topics directly improve discovery **within GitHub**: topic pages, the `topic:` search qualifier, and related-project surfaces. They are public metadata that search engines and AI assistants can read, but they are not a guaranteed external ranking factor — treat external SEO benefits as secondary and focus on accurate classification.

### Which GitHub topics should I add to my repository?

The ones that comparable repositories in your niche actually use and that your project genuinely supports. That is exactly what this tool measures: run `github-topic-recommender analyze OWNER/REPO` and review the evidence behind each recommendation.

### Does GitHub Topic Recommender use AI or an LLM?

No. The pipeline is deterministic: keyword extraction, GitHub search, counting, and a fixed scoring formula. The same input and search results always produce the same recommendations. See [docs/recommend-command.md](docs/recommend-command.md).

### Is GitHub Topic Recommender free?

Yes. It is open source and uses only the public GitHub REST API. An optional free personal access token raises API rate limits.

### Can it analyze a project that is not on GitHub yet?

Yes — use `github-topic-recommender recommend --description "..."` with a plain-text description. This is useful for choosing topics before publishing a new repository.

## Limitations

- GitHub topics are assigned by repository maintainers and may be incomplete or inconsistent.
- Popular repositories can disproportionately influence topic rankings.
- Search results may not represent every repository in a niche.
- New fields may not yet have established GitHub topics.
- Similar topic names do not always represent identical concepts.
- Stars are an imperfect proxy for project quality or relevance.
- Topic recommendations cannot guarantee higher traffic or search-engine rankings.
- Repository content should support every assigned topic.

Reports should disclose sample size, data collection time, filters, and confidence levels whenever possible.

## Roadmap

- [x] Analyze repository descriptions and README files
- [x] Search for comparable GitHub repositories
- [x] Collect and normalize repository topics
- [x] Calculate topic frequency and niche prevalence
- [ ] Calculate global and niche-specific topic lift
- [ ] Build a topic co-occurrence graph
- [ ] Add semantic repository matching
- [x] Generate explainable topic recommendations
- [ ] Detect redundant and unsupported topics
- [ ] Track topic popularity over time
- [ ] Export reports as JSON, CSV, and Markdown (JSON and Markdown available)
- [x] Provide a command-line interface
- [ ] Provide a web interface
- [ ] Provide a reusable API
- [ ] Add repository topic audits
- [ ] Add organization-wide repository analysis

