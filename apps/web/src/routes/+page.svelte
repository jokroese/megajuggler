<script lang="ts">
  import { onMount } from "svelte";
  import { loadKnownIds, saveKnownIds } from "$lib/progress";
  import { bucketTricks, type Trick, trickTitleById } from "$lib/tricks";

  let tricks = $state<Trick[]>([]);
  let knownIds = $state<Set<string>>(new Set());
  let isLoading = $state(true);
  let error = $state<string | null>(null);

  let buckets = $derived(bucketTricks(tricks, knownIds));
  let titles = $derived(trickTitleById(tricks));

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
    <section aria-labelledby="known-heading">
      <h2 id="known-heading">Known</h2>
      {#if buckets.known.length === 0}
        <p>No known tricks yet.</p>
      {:else}
        <div class="trick-list">
          {#each buckets.known as trick (trick.id)}
            <article class="trick-card">
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
                {#if trick.object_count}
                  <span>{trick.object_count} balls</span>
                {/if}
                {#if trick.difficulty}
                  <span>Difficulty {trick.difficulty}/10</span>
                {/if}
                {#if trick.siteswap}
                  <code>{trick.siteswap}</code>
                {/if}
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
        <p>No learnable tricks right now.</p>
      {:else}
        <div class="trick-list">
          {#each buckets.learnable as trick (trick.id)}
            <article class="trick-card">
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
                {#if trick.object_count}
                  <span>{trick.object_count} balls</span>
                {/if}
                {#if trick.difficulty}
                  <span>Difficulty {trick.difficulty}/10</span>
                {/if}
                {#if trick.siteswap}
                  <code>{trick.siteswap}</code>
                {/if}
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
        <p>No blocked tricks.</p>
      {:else}
        <div class="trick-list">
          {#each buckets.blocked as trick (trick.id)}
            <article class="trick-card">
              <strong>{trick.title}</strong>
              <div class="meta">
                {#if trick.object_count}
                  <span>{trick.object_count} balls</span>
                {/if}
                {#if trick.difficulty}
                  <span>Difficulty {trick.difficulty}/10</span>
                {/if}
                {#if trick.siteswap}
                  <code>{trick.siteswap}</code>
                {/if}
              </div>
              {#if trick.prerequisites.length > 0}
                <p>Missing: {missingPrerequisiteTitles(trick)}</p>
              {/if}
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

  .trick-list {
    display: grid;
    gap: 0.75rem;
  }

  .trick-card {
    border: 1px solid color-mix(in srgb, currentColor 20%, transparent);
    border-radius: 0.75rem;
    padding: 1rem;
  }

  label {
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

  code {
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
  }
</style>
