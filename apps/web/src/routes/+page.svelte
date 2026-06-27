<script lang="ts">
  import { onMount } from "svelte";
  import {
    createProgressExport,
    loadKnownIds,
    parseProgressImport,
    saveKnownIds,
    serialiseProgress,
  } from "$lib/progress";
  import TrickCard from "$lib/TrickCard.svelte";
  import {
    availableObjectCounts,
    bucketTricks,
    DEFAULT_TRICK_FILTERS,
    type DifficultyFilter,
    filterTricks,
    missingPrerequisiteIds,
    prerequisiteTitles,
    type Trick,
    trickTitleById,
    unlockCountsByTrickId,
  } from "$lib/tricks";

  type ViewMode = "learn" | "practice" | "explore";
  let tricks = $state<Trick[]>([]);
  let knownIds = $state<Set<string>>(new Set());
  let isLoading = $state(true);
  let error = $state<string | null>(null);
  let importMessage = $state<string | null>(null);
  let query = $state(DEFAULT_TRICK_FILTERS.query);
  let objectCount = $state<number | "all">(DEFAULT_TRICK_FILTERS.objectCount);
  let difficulty = $state<DifficultyFilter>(DEFAULT_TRICK_FILTERS.difficulty);
  let viewMode = $state<ViewMode>("explore");

  let filters = $derived({
    query,
    objectCount,
    difficulty,
  });
  let visibleTricks = $derived(filterTricks(tricks, filters));
  let buckets = $derived(bucketTricks(visibleTricks, knownIds));
  let titles = $derived(trickTitleById(tricks));
  let objectCounts = $derived(availableObjectCounts(tricks));
  let unlockCounts = $derived(unlockCountsByTrickId(tricks));
  let isFiltered = $derived(
    query.trim() !== "" ||
      objectCount !== DEFAULT_TRICK_FILTERS.objectCount ||
      difficulty !== DEFAULT_TRICK_FILTERS.difficulty,
  );
  let visibleIntentCount = $derived(
    viewMode === "learn"
      ? buckets.learnable.length
      : viewMode === "practice"
        ? buckets.known.length
        : visibleTricks.length,
  );
  let intentSummary = $derived(
    viewMode === "learn"
      ? `Showing ${visibleIntentCount} learnable trick${visibleIntentCount === 1 ? "" : "s"}${
          isFiltered ? " matching filters" : ""
        }.`
      : viewMode === "practice"
        ? `Showing ${visibleIntentCount} known trick${visibleIntentCount === 1 ? "" : "s"}${
            isFiltered ? " matching filters" : ""
          }.`
        : `Showing ${visibleIntentCount} trick${visibleIntentCount === 1 ? "" : "s"}${
            isFiltered ? " matching filters" : ""
          }.`,
  );
  let progressSummary = $derived(
    `${buckets.known.length} known · ${buckets.learnable.length} learnable · ${buckets.blocked.length} blocked`,
  );

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

  function titleForTrickId(id: string): string {
    return titles.get(id) ?? id;
  }

  function missingPrerequisiteTitlesList(trick: Trick): string[] {
    return missingPrerequisiteIds(trick, knownIds).map(titleForTrickId);
  }

  function unlocksInsight(trick: Trick): string | null {
    const unlockCount = unlockCounts.get(trick.id) ?? 0;
    if (unlockCount === 0) {
      return null;
    }

    return `This trick unlocks ${unlockCount} other trick${unlockCount === 1 ? "" : "s"}.`;
  }

  function blockedPathInsight(trick: Trick): string | null {
    const missing = missingPrerequisiteTitlesList(trick);
    if (missing.length === 0) {
      return null;
    }

    const firstMissing = missing[0];
    if (missing.length === 1) {
      return `Learn ${firstMissing} to unlock.`;
    }

    return `Start with ${firstMissing} to work towards ${trick.title}.`;
  }

  function missingPrerequisiteCountInsight(trick: Trick): string | null {
    const missingCount = missingPrerequisiteIds(trick, knownIds).length;
    if (missingCount <= 1) {
      return null;
    }

    return `${missingCount} prerequisites missing.`;
  }

  function compactInsights(insights: Array<string | null>): string[] {
    return insights.filter((insight): insight is string => insight !== null);
  }

  function cardInsights(trick: Trick): string[] {
    return compactInsights([unlocksInsight(trick)]);
  }

  function blockedLineageMode(trick: Trick): "missing" | "none" {
    return missingPrerequisiteIds(trick, knownIds).length > 1 ? "missing" : "none";
  }

  function blockedLineageText(trick: Trick): string {
    if (blockedLineageMode(trick) === "none") {
      return "";
    }

    return missingPrerequisiteTitles(trick);
  }

  function blockedCardInsights(trick: Trick): string[] {
    return compactInsights([
      blockedPathInsight(trick),
      missingPrerequisiteCountInsight(trick),
      unlocksInsight(trick),
    ]);
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
        <h2 id="controls-heading">What are you here to do?</h2>
        <p>{intentSummary}</p>
        <p class="progress-summary">{progressSummary}</p>
      </div>
      <fieldset class="mode-switcher">
        <legend>Mode</legend>
        <label>
          <input type="radio" name="view-mode" value="explore" bind:group={viewMode} />
          <span>
            <strong>Explore</strong>
            <small>Show known, learnable, and blocked tricks together.</small>
          </span>
        </label>
        <label>
          <input type="radio" name="view-mode" value="learn" bind:group={viewMode} />
          <span>
            <strong>Learn next</strong>
            <small>Show tricks where all prerequisites are known.</small>
          </span>
        </label>
        <label>
          <input type="radio" name="view-mode" value="practice" bind:group={viewMode} />
          <span>
            <strong>Practice</strong>
            <small>Show tricks you already know.</small>
          </span>
        </label>
      </fieldset>

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
          Balls
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

    {#if viewMode === "learn"}
      <section aria-labelledby="learn-next-heading">
        <h2 id="learn-next-heading">Learn next</h2>
        <p>Tricks where you already know every prerequisite.</p>
        {#if buckets.learnable.length === 0}
          <p>No learnable tricks match the current filters.</p>
        {:else}
          <div class="trick-list">
            {#each buckets.learnable as trick (trick.id)}
              <TrickCard
                {trick}
                checkboxId={`trick-learnable-${trick.id}`}
                checked={knownIds.has(trick.id)}
                showCheckbox
                lineageMode={trick.prerequisites.length > 0 ? "from" : "none"}
                lineageText={allPrerequisiteTitles(trick)}
                insights={cardInsights(trick)}
                onKnownChange={setKnown}
              />
            {/each}
          </div>
        {/if}
      </section>
    {:else if viewMode === "practice"}
      <section aria-labelledby="known-heading">
        <h2 id="known-heading">Practice</h2>
        <p>Tricks you already know.</p>
        {#if buckets.known.length === 0}
          <p>No known tricks match the current filters.</p>
        {:else}
          <div class="trick-list">
            {#each buckets.known as trick (trick.id)}
              <TrickCard
                {trick}
                checkboxId={`trick-known-${trick.id}`}
                checked={knownIds.has(trick.id)}
                showCheckbox
                insights={cardInsights(trick)}
                onKnownChange={setKnown}
              />
            {/each}
          </div>
        {/if}
      </section>
    {:else}
      <section aria-labelledby="known-heading">
        <h2 id="known-heading">Known</h2>
        {#if buckets.known.length === 0}
          <p>No known tricks match the current filters.</p>
        {:else}
          <div class="trick-list">
            {#each buckets.known as trick (trick.id)}
              <TrickCard
                {trick}
                checkboxId={`trick-known-${trick.id}`}
                checked={knownIds.has(trick.id)}
                showCheckbox
                insights={cardInsights(trick)}
                onKnownChange={setKnown}
              />
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
              <TrickCard
                {trick}
                checkboxId={`trick-learnable-${trick.id}`}
                checked={knownIds.has(trick.id)}
                showCheckbox
                lineageMode={trick.prerequisites.length > 0 ? "from" : "none"}
                lineageText={allPrerequisiteTitles(trick)}
                insights={cardInsights(trick)}
                onKnownChange={setKnown}
              />
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
              <TrickCard
                {trick}
                lineageMode={blockedLineageMode(trick)}
                lineageText={blockedLineageText(trick)}
                insights={blockedCardInsights(trick)}
              />
            {/each}
          </div>
        {/if}
      </section>
    {/if}
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

  .progress-summary {
    margin-top: -0.5rem;
    opacity: 0.75;
  }

  .filters,
  .progress-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    margin-top: 1rem;
  }

  .mode-switcher {
    display: grid;
    gap: 0.5rem;
    border: 0;
    margin: 1rem 0 0;
    padding: 0;
  }
  .mode-switcher legend {
    font-weight: 700;
  }
  .mode-switcher label {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 0.75rem;
    align-items: start;
    border: 1px solid color-mix(in srgb, currentColor 20%, transparent);
    border-radius: 0.75rem;
    padding: 0.75rem;
    cursor: pointer;
  }
  .mode-switcher label:has(input:checked) {
    border-color: currentColor;
    background: color-mix(in srgb, currentColor 7%, transparent);
  }
  .mode-switcher span {
    display: grid;
    gap: 0.15rem;
  }
  .mode-switcher small {
    opacity: 0.75;
  }

  @media (min-width: 48rem) {
    .mode-switcher {
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }
    .mode-switcher legend {
      grid-column: 1 / -1;
    }
  }

  .filters > label,
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
</style>
