<template>
  <div>
    <slot v-bind="{ open, close }" />
    <v-dialog
      v-model="dialog"
      max-width="988px"
      content-class="top-dialog"
      :scrollable="false"
    >
      <v-app-bar
        sticky
        dark
        color="primary-lighten-1 top-0 position-relative left-0"
        :rounded="!$vuetify.display.xs"
      >
        <v-text-field
          id="arrow-search"
          v-model="search.query.value"
          autofocus
          variant="solo"
          flat
          autocomplete="off"
          bg-color="primary-lighten-1"
          color="white"
          density="compact"
          class="mx-2 arrow-search"
          hide-details
          single-line
          :placeholder="$t('search.search')"
          :prepend-inner-icon="$globals.icons.search"
        />

        <v-btn
          v-if="$vuetify.display.xs"
          size="x-small"
          class="rounded-circle"
          light
          @click="dialog = false"
        >
          <v-icon>
            {{ $globals.icons.close }}
          </v-icon>
        </v-btn>
      </v-app-bar>
      <v-card
        class="position-relative mt-1 pa-1 scroll"
        max-height="700px"
        relative
        :loading="loading"
      >
        <v-card-actions>
          <div class="mr-auto">
            {{ $t("search.results") }}
          </div>
          <!-- <router-link
            :to="advancedSearchUrl"
            class="text-primary"
          > {{ $t("search.advanced-search") }} </router-link> -->
        </v-card-actions>

        <RecipeCardMobile
          v-for="(recipe, index) in search.data.value"
          :key="index"
          :tabindex="index"
          class="ma-1 arrow-nav"
          :name="recipe.name ?? ''"
          :description="recipe.description ?? ''"
          :slug="recipe.slug ?? ''"
          :rating="recipe.rating ?? 0"
          :image="recipe.image"
          :recipe-id="recipe.id ?? ''"
          v-bind="$attrs.selected ? { selected: () => handleSelect(recipe) } : {}"
        />
      </v-card>
    </v-dialog>
  </div>
</template>

<script lang="ts">
import RecipeCardMobile from "./RecipeCardMobile.vue";
import { useLoggedInState } from "~/composables/use-logged-in-state";
import type { RecipeSummary } from "~/lib/api/types/recipe";
import { useUserApi } from "~/composables/api";
import { useRecipeSearch } from "~/composables/recipes/use-recipe-search";
import { usePublicExploreApi } from "~/composables/api/api-client";

const SELECTED_EVENT = "selected";
export default defineNuxtComponent({
  components: {
    RecipeCardMobile,
  },

  setup(_, context) {
    const $auth = useMealieAuth();
    const state = reactive({
      loading: false,
      selectedIndex: -1,
    });

    // ===========================================================================
    // Dialog State Management
    const dialog = ref(false);

    // Reset or Grab Recipes on Change
    watch(dialog, (val) => {
      if (!val) {
        search.query.value = "";
        state.selectedIndex = -1;
        search.data.value = [];
      }
    });

    // ===========================================================================
    // Event Handlers

    function selectRecipe() {
      const recipeCards = document.getElementsByClassName("arrow-nav");
      if (recipeCards) {
        if (state.selectedIndex < 0) {
          state.selectedIndex = -1;
          document.getElementById("arrow-search")?.focus();
          return;
        }

        if (state.selectedIndex >= recipeCards.length) {
          state.selectedIndex = recipeCards.length - 1;
        }

        (recipeCards[state.selectedIndex] as HTMLElement).focus();
      }
    }

    function onUpDown(e: KeyboardEvent) {
      if (e.key === "Enter") {
        console.log(document.activeElement);
        // (document.activeElement as HTMLElement).click();
      }
      else if (e.key === "ArrowUp") {
        e.preventDefault();
        state.selectedIndex--;
      }
      else if (e.key === "ArrowDown") {
        e.preventDefault();
        state.selectedIndex++;
      }
      else {
        return;
      }
      selectRecipe();
    }

    watch(dialog, (val) => {
      if (!val) {
        document.removeEventListener("keyup", onUpDown);
      }
      else {
        document.addEventListener("keyup", onUpDown);
      }
    });

    const groupSlug = computed(() => route.params.groupSlug as string || $auth.user.value?.groupSlug || "");
    const route = useRoute();
    const advancedSearchUrl = computed(() => `/g/${groupSlug.value}`);
    watch(route, close);

    function open() {
      dialog.value = true;
    }
    function close() {
      dialog.value = false;
    }

    // ===========================================================================
    // Basic Search
    const { isOwnGroup } = useLoggedInState();
    const api = isOwnGroup.value ? useUserApi() : usePublicExploreApi(groupSlug.value).explore;
    const search = useRecipeSearch(api);

    // Select Handler

    function handleSelect(recipe: RecipeSummary) {
      close();
      context.emit(SELECTED_EVENT, recipe);
    }

    return {
      ...toRefs(state),
      advancedSearchUrl,
      dialog,
      open,
      close,
      handleSelect,
      search,
    };
  },
});
</script>

<style>
.scroll {
  overflow-y: auto;
}
</style>
