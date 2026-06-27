<script lang="ts">
  import { onMount } from "svelte";
  import {
    createProgressExport,
    loadKnownIds,
    parseProgressImport,
    saveKnownIds,
    serialiseProgress,
  } from "$lib/progress";
  import {
    availableObjectCounts,
    bucketTricks,
    DEFAULT_TRICK_FILTERS,
    type DifficultyFilter,
    filterTricks,
    prerequisiteTitles,
    type Trick,
    trickTitleById,
  } from "$lib/tricks";

  let tricks = $state<Trick[]>([]);
  let knownIds = $state<Set<string>>(new Set());
  let isLoading = $state(true);
  let error = $state<string | null>(null);
  let importMessage = $state<string | null>(null);
  let query = $state(DEFAULT_TRICK_FILTERS.query);
  let objectCount = $state<number | "all">(DEFAULT_TRICK_FILTERS.objectCount);
  let difficulty = $state<DifficultyFilter>(DEFAULT_TRICK_FILTERS.difficulty);

  let filters = $derived({
    query,
    objectCount,
    difficulty,
  });
  let visibleTricks = $derived(filterTricks(tricks, filters));
  let buckets = $derived(bucketTricks(visibleTricks, knownIds));
  let titles = $derived(trickTitleById(tricks));
  let objectCounts = $derived(availableObjectCounts(tricks));

  onMount(async () => {
    try {
      const response = await fetch("/data/tricks.json");
      if (!response.ok) {
        throw new Error(`Failed to load tricks.json: ${response.status}`);
      }
      tricks = await response.json();
      knownIds = loadKnownIds();
    } catch (caught) {
      error = caught instanceof Error ? caught.message : "Failed to load tricks.";
    } finally {
      isLoading = false;
    }
  });

  function setKnown(id: string, known: boolean) {
    const next = new Set(knownIds);
    if (known) {
      next.add(id);
    } else {
      next.delete(id);
    }
    knownIds = next;
    saveKnownIds(knownIds);
  }

  function missingPrerequisiteTitles(trick: Trick): string {
    return trick.prerequisites
      .filter((id) => !knownIds.has(id))
      .map((id) => titles.get(id) ?? id)
      .join(", ");
  }

  function allPrerequisiteTitles(trick: Trick): string {
    return prerequisiteTitles(trick, titles).join(", ");
  }

  function clearFilters() {
    query = DEFAULT_TRICK_FILTERS.query;
    objectCount = DEFAULT_TRICK_FILTERS.objectCount;
    difficulty = DEFAULT_TRICK_FILTERS.difficulty;
  }

  function exportProgress() {
    const json = serialiseProgress(knownIds);
    const blob = new Blob([json], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const exportedAt = createProgressExport(knownIds).exportedAt.slice(0, 10);
    const link = document.createElement("a");
    link.href = url;
    link.download = `megajuggler-progress-${exportedAt}.json`;
    link.click();
    URL.revokeObjectURL(url);
  }

  async function importProgress(event: Event) {
    const input = event.currentTarget;
    if (!(input instanceof HTMLInputElement)) {
      return;
    }

    const file = input.files?.[0];
    input.value = "";
    if (!file) {
      return;
    }

    try {
      const importedIds = parseProgressImport(await file.text());
      knownIds = importedIds;
      saveKnownIds(knownIds);
      importMessage = `Imported ${knownIds.size} known trick${knownIds.size === 1 ? "" : "s"}.`;
    } catch (caught) {
      importMessage = caught instanceof Error ? caught.message : "Could not import progress file.";
    }
  }
</script>

<svelte:head>
  <title>Megajuggler</title>
  <meta name="description" content="Track juggling tricks and find what to learn next." />
</svelte:head>

<main>
  <header>
    <h1>Megajuggler</h1>
    <p>Track the tricks you know and discover what you can learn next.</p>
  </header>

  {#if isLoading}
    <p>Loading tricks…</p>
  {:else if error}
    <p role="alert">{error}</p>
  {:else}
    <section aria-labelledby="controls-heading" class="controls">
      <div>
        <h2 id="controls-heading">Controls</h2>
        <p>
          Showing {visibleTricks.length} of {tricks.length} tricks.
          {knownIds.size} known.
        </p>
      </div>

      <div class="filters">
        <label>
          Search
          <input
            type="search"
            bind:value={query}
            placeholder="Search title, ID, or siteswap"
            autocomplete="off"
          />
        </label>

        <label>
          Objects
          <select bind:value={objectCount}>
            <option value="all">All</option>
            {#each objectCounts as count}
              <option value={count}>{count} balls</option>
            {/each}
          </select>
        </label>

        <label>
          Difficulty
          <select bind:value={difficulty}>
            <option value="all">All</option>
            <option value="easy">Easy, 1–3</option>
            <option value="medium">Medium, 4–6</option>
            <option value="hard">Hard, 7–10</option>
            <option value="unknown">Unknown</option>
          </select>
        </label>

        <button type="button" onclick={clearFilters}>Clear filters</button>
      </div>

      <div class="progress-actions">
        <button type="button" onclick={exportProgress}>Export progress</button>
        <label class="import-button">
          Import progress
          <input type="file" accept="application/json,.json" onchange={importProgress} />
        </label>
      </div>

      {#if importMessage}
        <p role="status">{importMessage}</p>
      {/if}
    </section>

    <section aria-labelledby="known-heading">
      <h2 id="known-heading">Known</h2>
      {#if buckets.known.length === 0}
        <p>No known tricks match the current filters.</p>
      {:else}
        <div class="trick-list">
          {#each buckets.known as trick (trick.id)}
            <article class="trick-card">
              {#if trick.animation_url}
                <img
                  class="trick-animation"
                  src={trick.animation_url}
                  alt=""
                  loading="lazy"
                  width="160"
                />
              {/if}
              <div class="trick-content">
                <!-- biome-ignore lint/a11y/noLabelWithoutControl: checkbox and title are nested in the label -->
                <label for={`trick-known-${trick.id}`}>
                  <input
                    id={`trick-known-${trick.id}`}
                    type="checkbox"
                    checked={knownIds.has(trick.id)}
                    onchange={(event) => setKnown(trick.id, event.currentTarget.checked)}
                  />
                  <strong>{trick.title}</strong>
                </label>
                <div class="meta">
                  {#if trick.category}
                    <span>{trick.category}</span>
                  {/if}
                  {#if trick.difficulty}
                    <span>Difficulty {trick.difficulty}/10</span>
                  {/if}
                  {#if trick.siteswap}
                    <code>{trick.siteswap}</code>
                  {/if}
                </div>
                {#if trick.description_preview}
                  <p class="description-preview">{trick.description_preview}</p>
                {/if}
                <p class="links">
                  <a href={trick.source_url} target="_blank" rel="noreferrer">Open LoJ page</a>
                </p>
              </div>
            </article>
          {/each}
        </div>
      {/if}
    </section>

    <section aria-labelledby="learn-next-heading">
      <h2 id="learn-next-heading">Learn next</h2>
      <p>Tricks where you already know every prerequisite.</p>
      {#if buckets.learnable.length === 0}
        <p>No learnable tricks match the current filters.</p>
      {:else}
        <div class="trick-list">
          {#each buckets.learnable as trick (trick.id)}
            <article class="trick-card">
              {#if trick.animation_url}
                <img
                  class="trick-animation"
                  src={trick.animation_url}
                  alt=""
                  loading="lazy"
                  width="160"
                />
              {/if}
              <div class="trick-content">
                <!-- biome-ignore lint/a11y/noLabelWithoutControl: checkbox and title are nested in the label -->
                <label for={`trick-learnable-${trick.id}`}>
                  <input
                    id={`trick-learnable-${trick.id}`}
                    type="checkbox"
                    checked={knownIds.has(trick.id)}
                    onchange={(event) => setKnown(trick.id, event.currentTarget.checked)}
                  />
                  <strong>{trick.title}</strong>
                </label>
                <div class="meta">
                  {#if trick.category}
                    <span>{trick.category}</span>
                  {/if}
                  {#if trick.difficulty}
                    <span>Difficulty {trick.difficulty}/10</span>
                  {/if}
                  {#if trick.siteswap}
                    <code>{trick.siteswap}</code>
                  {/if}
                </div>
                {#if trick.prerequisites.length > 0}
                  <p class="lineage">Prerequisites: {allPrerequisiteTitles(trick)}</p>
                {/if}
                {#if trick.description_preview}
                  <p class="description-preview">{trick.description_preview}</p>
                {/if}
                <p class="links">
                  <a href={trick.source_url} target="_blank" rel="noreferrer">Open LoJ page</a>
                </p>
              </div>
            </article>
          {/each}
        </div>
      {/if}
    </section>

    <section aria-labelledby="blocked-heading">
      <h2 id="blocked-heading">Blocked</h2>
      <p>Tricks where at least one prerequisite is still missing.</p>
      {#if buckets.blocked.length === 0}
        <p>No blocked tricks match the current filters.</p>
      {:else}
        <div class="trick-list">
          {#each buckets.blocked as trick (trick.id)}
            <article class="trick-card">
              {#if trick.animation_url}
                <img
                  class="trick-animation"
                  src={trick.animation_url}
                  alt=""
                  loading="lazy"
                  width="160"
                />
              {/if}
              <div class="trick-content">
                <strong>{trick.title}</strong>
                <div class="meta">
                  {#if trick.category}
                    <span>{trick.category}</span>
                  {/if}
                  {#if trick.difficulty}
                    <span>Difficulty {trick.difficulty}/10</span>
                  {/if}
                  {#if trick.siteswap}
                    <code>{trick.siteswap}</code>
                  {/if}
                </div>
                {#if trick.prerequisites.length > 0}
                  <p class="lineage">Prerequisites: {allPrerequisiteTitles(trick)}</p>
                  <p>Missing: {missingPrerequisiteTitles(trick)}</p>
                {/if}
                {#if trick.description_preview}
                  <p class="description-preview">{trick.description_preview}</p>
                {/if}
                <p class="links">
                  <a href={trick.source_url} target="_blank" rel="noreferrer">Open LoJ page</a>
                </p>
              </div>
            </article>
          {/each}
        </div>
      {/if}
    </section>
  {/if}
</main>

<style>
  main {
    max-width: 72rem;
    margin: 0 auto;
    padding: 2rem;
  }

  header {
    margin-bottom: 2rem;
  }

  section {
    margin-block: 2rem;
  }

  .controls {
    border: 1px solid color-mix(in srgb, currentColor 20%, transparent);
    border-radius: 0.75rem;
    padding: 1rem;
  }

  .filters,
  .progress-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    margin-top: 1rem;
  }

  .filters label,
  .import-button {
    display: grid;
    gap: 0.25rem;
  }

  input,
  select,
  button,
  .import-button {
    font: inherit;
  }

  input,
  select {
    min-height: 2.25rem;
  }

  button,
  .import-button {
    border: 1px solid color-mix(in srgb, currentColor 25%, transparent);
    border-radius: 0.5rem;
    background: transparent;
    color: inherit;
    cursor: pointer;
    padding: 0.45rem 0.7rem;
  }

  .import-button input {
    inline-size: 1px;
    block-size: 1px;
    opacity: 0;
    position: absolute;
    pointer-events: none;
  }

  .trick-list {
    display: grid;
    gap: 0.75rem;
  }

  .trick-card {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 1rem;
    border: 1px solid color-mix(in srgb, currentColor 20%, transparent);
    border-radius: 0.75rem;
    padding: 1rem;
  }

  .trick-content {
    min-width: 0;
  }

  .trick-animation {
    inline-size: 10rem;
    max-inline-size: 30vw;
    block-size: auto;
    border-radius: 0.5rem;
    background: color-mix(in srgb, currentColor 5%, transparent);
  }

  .trick-card label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .meta {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 0.5rem;
    opacity: 0.8;
  }

  .lineage,
  .description-preview,
  .links {
    margin-block: 0.75rem 0;
  }

  .lineage {
    font-size: 0.95rem;
  }

  .description-preview {
    max-width: 60rem;
  }

  .links {
    display: flex;
    flex-wrap: wrap;
    gap: 0.35rem;
  }

  code {
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
  }

  @media (max-width: 42rem) {
    .trick-card {
      grid-template-columns: 1fr;
    }

    .trick-animation {
      inline-size: 100%;
      max-inline-size: 20rem;
    }
  }
</style>
