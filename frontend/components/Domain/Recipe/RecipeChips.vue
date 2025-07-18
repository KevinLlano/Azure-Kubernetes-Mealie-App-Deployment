<template>
  <div v-if="items.length > 0">
    <h2
      v-if="title"
      class="mt-4"
    >
      {{ title }}
    </h2>
    <v-chip
      v-for="category in items.slice(0, limit)"
      :key="category.name"
      label
      class="mr-1 mt-1"
      color="accent"
      variant="flat"
      :size="small ? 'small' : 'default'"
      dark

      @click.prevent="() => $emit('item-selected', category, urlPrefix)"
    >
      {{ truncateText(category.name) }}
    </v-chip>
  </div>
</template>

<script lang="ts">
import type { RecipeCategory, RecipeTag, RecipeTool } from "~/lib/api/types/recipe";

export type UrlPrefixParam = "tags" | "categories" | "tools";

export default defineNuxtComponent({
  props: {
    truncate: {
      type: Boolean,
      default: false,
    },
    items: {
      type: Array as () => RecipeCategory[] | RecipeTag[] | RecipeTool[],
      default: () => [],
    },
    title: {
      type: Boolean,
      default: false,
    },
    urlPrefix: {
      type: String as () => UrlPrefixParam,
      default: "categories",
    },
    limit: {
      type: Number,
      default: 999,
    },
    small: {
      type: Boolean,
      default: false,
    },
    maxWidth: {
      type: String,
      default: null,
    },
  },
  emits: ["item-selected"],
  setup(props) {
    const $auth = useMealieAuth();

    const route = useRoute();
    const groupSlug = computed(() => route.params.groupSlug || $auth.user.value?.groupSlug || "");
    const baseRecipeRoute = computed<string>(() => {
      return `/g/${groupSlug.value}`;
    });

    function truncateText(text: string, length = 20, clamp = "...") {
      if (!props.truncate) return text;
      const node = document.createElement("div");
      node.innerHTML = text;
      const content = node.textContent || "";
      return content.length > length ? content.slice(0, length) + clamp : content;
    }

    return {
      baseRecipeRoute,
      truncateText,
    };
  },
});
</script>

<style></style>
