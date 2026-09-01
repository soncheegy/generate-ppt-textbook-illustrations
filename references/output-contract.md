# Output contract

## Two stages

Stage one produces `illustration-tasks.json` and `review.txt`. Stage two begins only after approval and produces the image directories plus `qa-report.json`.

## Directory and naming rules

Use these type directories:

- `底层图/`
- `剧情图/`
- `氛围图/`
- `元素图/`

Use the PPT page pair as the filename prefix. Number multiple tasks of the same type from 1 in slide reading order:

- one bottom layer: `1-2底层.png`
- three plot images: `3-4剧情1.png`, `3-4剧情2.png`, `3-4剧情3.png`
- two atmosphere assets: `11-12氛围1.png`, `11-12氛围2.png`
- three elements: `15-16元素1.png`, `15-16元素2.png`, `15-16元素3.png`

When a page pair has exactly one plot image, omit the numeric suffix unless the approved plan explicitly retains it. Atmosphere and element assets always use numeric suffixes.

## Manifest review

For every task verify:

- `type` and `relative_path`;
- source slide and page pair;
- one asset per blue plot box;
- one isolated asset per clearly separated atmosphere/element noun phrase;
- raw PPT description preserved in `source_text`;
- named characters listed in `characters`;
- aspect ratio and transparency contract;
- warnings resolved before approval.

Do not silently discard an ambiguous item. Revise the JSON manifest when the user clarifies or approves a split/merge.

## Generation ledger

During stage two keep a concise ledger outside the skill folder with:

- task id and filename;
- final prompt;
- reference images used and their roles;
- generation status;
- revisions made;
- final QA result.

## Final report

Report:

- generated/approved count by type;
- output root;
- manifest path and QA report path;
- any approved deviation from the PPT or filename contract.
