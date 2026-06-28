<script lang="ts">
  import { animationUrl, descriptionPreview, type Trick } from "./tricks";

  type LineageMode = "from" | "missing" | "none";

  let {
    trick,
    checked = false,
    checkboxId,
    showCheckbox = false,
    lineageMode = "none",
    lineageText = "",
    insights = [],
    onKnownChange,
  }: {
    trick: Trick;
    checked?: boolean;
    checkboxId?: string;
    showCheckbox?: boolean;
    lineageMode?: LineageMode;
    lineageText?: string;
    insights?: string[];
    onKnownChange?: (id: string, known: boolean) => void;
  } = $props();

  let preview = $derived(descriptionPreview(trick.description));

  function handleKnownChange(event: Event) {
    if (!onKnownChange) {
      return;
    }

    const input = event.currentTarget;
    if (!(input instanceof HTMLInputElement)) {
      return;
    }

    onKnownChange(trick.id, input.checked);
  }
</script>

<article class="trick-card">
  <video
    class="trick-animation"
    autoplay
    loop
    muted
    playsinline
    preload="metadata"
    width="160"
    aria-label={`${trick.title} animation`}
  >
    <source src={animationUrl(trick, "webm")} type="video/webm" />
    <source src={animationUrl(trick, "mp4")} type="video/mp4" />
  </video>

  <div class="trick-content">
    {#if showCheckbox}
      <label for={checkboxId}>
        <input
          id={checkboxId}
          type="checkbox"
          {checked}
          aria-label={`Mark ${trick.title} as known`}
          onchange={handleKnownChange}
        />
        <strong>{trick.title}</strong>
      </label>
    {:else}
      <strong>{trick.title}</strong>
    {/if}

    <div class="meta">
      {#if trick.object_count}
        <span>{trick.object_count} ball{trick.object_count === 1 ? "" : "s"}</span>
      {/if}
      {#if trick.difficulty}
        <span>Difficulty {trick.difficulty}/10</span>
      {/if}
      {#if trick.siteswap}
        <code>{trick.siteswap}</code>
      {/if}
    </div>

    {#if lineageMode !== "none" && lineageText}
      <p class="lineage">
        {lineageMode === "from" ? "From" : "Missing"}: {lineageText}
      </p>
    {/if}

    {#if insights.length > 0}
      <ul class="insights" aria-label={`${trick.title} learning hints`}>
        {#each insights as insight}
          <li>{insight}</li>
        {/each}
      </ul>
    {/if}

    {#if preview}
      <p class="description-preview">{preview}</p>
    {/if}

    <p class="links">
      <a href={trick.source_url} target="_blank" rel="noreferrer">Open LoJ page</a>
    </p>
  </div>
</article>

<style>
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

  .insights {
    display: grid;
    gap: 0.25rem;
    margin-block: 0.75rem 0;
    padding-inline-start: 1.25rem;
    font-size: 0.95rem;
  }

  .insights li::marker {
    color: color-mix(in srgb, currentColor 60%, transparent);
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
