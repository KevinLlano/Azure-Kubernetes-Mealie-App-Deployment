<template>
  <section @keyup.ctrl.z="undoMerge">
    <!-- Ingredient Link Editor -->
    <v-dialog
      v-if="dialog"
      v-model="dialog"
      width="600"
    >
      <v-card :ripple="false">
        <v-sheet
          color="primary"
          class="mt-n1 mb-3 pa-3 d-flex align-center"
          style="border-radius: 6px; width: 100%;"
        >
          <v-icon
            size="large"
            start
          >
            {{ $globals.icons.link }}
          </v-icon>
          <v-toolbar-title class="headline">
            {{ $t("recipe.ingredient-linker") }}
          </v-toolbar-title>
          <v-spacer />
        </v-sheet>

        <v-card-text class="pt-4">
          <p>
            {{ activeText }}
          </p>
          <v-divider class="mb-4" />
          <v-checkbox
            v-for="ing in unusedIngredients"
            :key="ing.referenceId"
            v-model="activeRefs"
            :value="ing.referenceId"
            class="mb-n2 mt-n2"
          >
            <template #label>
              <RecipeIngredientHtml :markup="parseIngredientText(ing, recipe.settings.disableAmount)" />
            </template>
          </v-checkbox>

          <template v-if="usedIngredients.length > 0">
            <h4 class="py-3 ml-1">
              {{ $t("recipe.linked-to-other-step") }}
            </h4>
            <v-checkbox
              v-for="ing in usedIngredients"
              :key="ing.referenceId"
              v-model="activeRefs"
              :value="ing.referenceId"
              class="mb-n2 mt-n2"
            >
              <template #label>
                <RecipeIngredientHtml :markup="parseIngredientText(ing, recipe.settings.disableAmount)" />
              </template>
            </v-checkbox>
          </template>
        </v-card-text>

        <v-divider />

        <v-card-actions>
          <BaseButton
            cancel
            @click="dialog = false"
          />
          <v-spacer />
          <div class="d-flex flex-wrap justify-end">
            <BaseButton
              class="my-1"
              color="info"
              @click="autoSetReferences"
            >
              <template #icon>
                {{ $globals.icons.robot }}
              </template>
              {{ $t("recipe.auto") }}
            </BaseButton>
            <BaseButton
              class="ml-2 my-1"
              save
              @click="setIngredientIds"
            />
            <BaseButton
              v-if="availableNextStep"
              class="ml-2 my-1"
              @click="saveAndOpenNextLinkIngredients"
            >
              <template #icon>
                {{ $globals.icons.forward }}
              </template>
              {{ $t("recipe.nextStep") }}
            </BaseButton>
          </div>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <div class="d-flex justify-space-between justify-start">
      <h2
        v-if="!isCookMode"
        class="mt-1 text-h5 font-weight-medium opacity-80"
      >
        {{ $t("recipe.instructions") }}
      </h2>
      <BaseButton
        v-if="!isEditForm && !isCookMode"
        minor
        cancel
        color="primary"
        @click="toggleCookMode()"
      >
        <template #icon>
          {{ $globals.icons.primary }}
        </template>
        {{ $t("recipe.cook-mode") }}
      </BaseButton>
    </div>
    <VueDraggable
      v-model="instructionList"
      :disabled="!isEditForm"
      handle=".handle"
      :delay="250"
      :delay-on-touch-only="true"
      v-bind="{
        animation: 200,
        group: 'recipe-instructions',
        ghostClass: 'ghost',
      }"
      @start="drag = true"
      @end="onDragEnd"
    >
      <TransitionGroup
        type="transition"
      >
        <div
          v-for="(step, index) in instructionList"
          :key="step.id!"
          class="list-group-item"
        >
          <v-sheet
            v-if="step.id && showTitleEditor[step.id]"
            color="primary"
            class="mt-6 mb-2 d-flex align-center"
            :class="isEditForm ? 'pa-2' : 'pa-3'"
            style="border-radius: 6px; cursor: pointer; width: 100%;"
            @click="toggleCollapseSection(index)"
          >
            <template v-if="isEditForm">
              <v-text-field
                v-model="step.title"
                class="pa-0"
                density="compact"
                variant="solo"
                flat
                :placeholder="$t('recipe.section-title')"
                bg-color="primary"
                hide-details
              />
            </template>
            <template v-else>
              <v-toolbar-title class="section-title-text">
                {{ step.title }}
              </v-toolbar-title>
            </template>
          </v-sheet>
          <v-hover v-slot="{ isHovering }">
            <v-card
              class="my-3"
              :class="[{ 'on-hover': isHovering }, isChecked(index)]"
              :elevation="isHovering ? 12 : 2"
              :ripple="false"
              @click="toggleDisabled(index)"
            >
              <v-card-title :class="{ 'pb-0': !isChecked(index) }">
                <div class="d-flex align-center">
                  <v-text-field
                    v-if="isEditForm"
                    v-model="step.summary"
                    class="headline handle"
                    hide-details
                    density="compact"
                    variant="solo"
                    flat
                    :placeholder="$t('recipe.step-index', { step: index + 1 })"
                  >
                    <template #prepend>
                      <v-icon size="26">
                        {{ $globals.icons.arrowUpDown }}
                      </v-icon>
                    </template>
                  </v-text-field>
                  <span v-else>
                    {{ step.summary ? step.summary : $t("recipe.step-index", { step: index + 1 }) }}
                  </span>
                  <template v-if="isEditForm">
                    <div class="ml-auto">
                      <BaseButtonGroup
                        :large="false"
                        :buttons="[
                          {
                            icon: $globals.icons.delete,
                            text: $t('general.delete'),
                            event: 'delete',
                          },
                          {
                            icon: $globals.icons.dotsVertical,
                            text: '',
                            event: 'open',
                            children: [
                              {
                                text: $t('recipe.toggle-section'),
                                event: 'toggle-section',
                              },
                              {
                                text: $t('recipe.link-ingredients'),
                                event: 'link-ingredients',
                              },
                              {
                                text: $t('recipe.upload-image'),
                                event: 'upload-image',
                              },
                              {
                                icon: previewStates[index] ? $globals.icons.edit : $globals.icons.eye,
                                text: previewStates[index] ? $t('recipe.edit-markdown') : $t('markdown-editor.preview-markdown-button-label'),
                                event: 'preview-step',
                                divider: true,
                              },
                              {
                                text: $t('recipe.merge-above'),
                                event: 'merge-above',
                              },
                              {
                                text: $t('recipe.move-to-top'),
                                event: 'move-to-top',
                              },
                              {
                                text: $t('recipe.move-to-bottom'),
                                event: 'move-to-bottom',
                              },
                              {
                                text: $t('recipe.insert-above'),
                                event: 'insert-above',
                              },
                              {
                                text: $t('recipe.insert-below'),
                                event: 'insert-below',
                              },
                            ],
                          },
                        ]"
                        @merge-above="mergeAbove(index - 1, index)"
                        @move-to-top="moveTo('top', index)"
                        @move-to-bottom="moveTo('bottom', index)"
                        @insert-above="insert(index)"
                        @insert-below="insert(index + 1)"
                        @toggle-section="toggleShowTitle(step.id!)"
                        @link-ingredients="openDialog(index, step.text, step.ingredientReferences)"
                        @preview-step="togglePreviewState(index)"
                        @upload-image="openImageUpload(index)"
                        @delete="instructionList.splice(index, 1)"
                      />
                    </div>
                  </template>
                  <v-fade-transition>
                    <v-icon
                      v-show="isChecked(index)"
                      size="24"
                      class="ml-auto"
                      color="success"
                    >
                      {{ $globals.icons.checkboxMarkedCircle }}
                    </v-icon>
                  </v-fade-transition>
                </div>
              </v-card-title>

              <v-progress-linear
                v-if="isEditForm && loadingStates[index]"
                :active="true"
                :indeterminate="true"
              />

              <!-- Content -->
              <DropZone @drop="(f) => handleImageDrop(index, f)">
                <v-card-text
                  v-if="isEditForm"
                  @click="$emit('click-instruction-field', `${index}.text`)"
                >
                  <MarkdownEditor
                    v-model="instructionList[index]['text']"
                    v-model:preview="previewStates[index]"
                    class="mb-2"
                    :display-preview="false"
                    :textarea="{
                      hint: $t('recipe.attach-images-hint'),
                      persistentHint: true,
                    }"
                  />
                  <RecipeIngredientHtml
                    v-for="ing in step.ingredientReferences"
                    :key="ing.referenceId!"
                    :markup="getIngredientByRefId(ing.referenceId!)"
                  />
                </v-card-text>
              </DropZone>
              <v-expand-transition>
                <div
                  v-if="!isChecked(index) && !isEditForm"
                  class="m-0 p-0"
                >
                  <v-card-text class="markdown">
                    <v-row>
                      <v-col
                        v-if="isCookMode && step.ingredientReferences && step.ingredientReferences.length > 0"
                        cols="12"
                        sm="5"
                      >
                        <div class="ml-n4">
                          <RecipeIngredients
                            :value="recipe.recipeIngredient.filter((ing) => {
                              if (!step.ingredientReferences) return false
                              return step.ingredientReferences.map((ref) => ref.referenceId).includes(ing.referenceId || '')
                            })"
                            :scale="scale"
                            :disable-amount="recipe.settings.disableAmount"
                            :is-cook-mode="isCookMode"
                          />
                        </div>
                      </v-col>
                      <v-divider
                        v-if="isCookMode && step.ingredientReferences && step.ingredientReferences.length > 0 && $vuetify.display.smAndUp"
                        vertical
                      />
                      <v-col>
                        <SafeMarkdown
                          class="markdown"
                          :source="step.text"
                        />
                      </v-col>
                    </v-row>
                  </v-card-text>
                </div>
              </v-expand-transition>
            </v-card>
          </v-hover>
        </div>
      </TransitionGroup>
    </VueDraggable>
    <v-divider
      v-if="!isCookMode"
      class="mt-10 d-flex d-md-none"
    />
  </section>
</template>

<script setup lang="ts">
import { VueDraggable } from "vue-draggable-plus";
import { computed, nextTick, onMounted, ref, watch } from "vue";
import RecipeIngredientHtml from "../../RecipeIngredientHtml.vue";
import type { RecipeStep, IngredientReferences, RecipeIngredient, RecipeAsset, Recipe } from "~/lib/api/types/recipe";
import { parseIngredientText } from "~/composables/recipes";
import { uuid4 } from "~/composables/use-utils";
import { useUserApi, useStaticRoutes } from "~/composables/api";
import { usePageState } from "~/composables/recipe-page/shared-state";
import { useExtractIngredientReferences } from "~/composables/recipe-page/use-extract-ingredient-references";
import type { NoUndefinedField } from "~/lib/api/types/non-generated";
import DropZone from "~/components/global/DropZone.vue";
import RecipeIngredients from "~/components/Domain/Recipe/RecipeIngredients.vue";

interface MergerHistory {
  target: number;
  source: number;
  targetText: string;
  sourceText: string;
}

const instructionList = defineModel<RecipeStep[]>("modelValue", { required: true, default: () => [] });
const assets = defineModel<RecipeAsset[]>("assets", { required: true, default: () => [] });

const props = defineProps({
  recipe: {
    type: Object as () => NoUndefinedField<Recipe>,
    required: true,
  },
  scale: {
    type: Number,
    default: 1,
  },
});

const emit = defineEmits(["click-instruction-field", "update:assets"]);

const BASE_URL = useRequestURL().origin;

const { isCookMode, toggleCookMode, isEditForm } = usePageState(props.recipe.slug);

const dialog = ref(false);
const disabledSteps = ref<number[]>([]);
const unusedIngredients = ref<RecipeIngredient[]>([]);
const usedIngredients = ref<RecipeIngredient[]>([]);

const showTitleEditor = ref<{ [key: string]: boolean }>({});

// ===============================================================
// UI State Helpers

function hasSectionTitle(title: string | undefined) {
  return !(title === null || title === "" || title === undefined);
}

watch(instructionList, (v) => {
  disabledSteps.value = [];

  v.forEach((element: RecipeStep) => {
    if (element.id !== undefined) {
      showTitleEditor.value[element.id!] = hasSectionTitle(element.title!);
    }
  });
}, { deep: true });

const showCookMode = ref(false);

onMounted(() => {
  instructionList.value.forEach((element: RecipeStep) => {
    if (element.id !== undefined) {
      showTitleEditor.value[element.id!] = hasSectionTitle(element.title!);
    }

    if (showCookMode.value === false && element.ingredientReferences && element.ingredientReferences.length > 0) {
      showCookMode.value = true;
    }

    showTitleEditor.value = { ...showTitleEditor.value };
  });

  if (assets.value === undefined) {
    emit("update:assets", []);
  }
});

function toggleDisabled(stepIndex: number) {
  if (isEditForm.value) {
    return;
  }
  if (disabledSteps.value.includes(stepIndex)) {
    const index = disabledSteps.value.indexOf(stepIndex);
    if (index !== -1) {
      disabledSteps.value.splice(index, 1);
    }
  }
  else {
    disabledSteps.value.push(stepIndex);
  }
}

function isChecked(stepIndex: number) {
  if (disabledSteps.value.includes(stepIndex) && !isEditForm.value) {
    return "disabled-card";
  }
}

function toggleShowTitle(id?: string) {
  if (!id) {
    return;
  }

  showTitleEditor.value[id] = !showTitleEditor.value[id];

  const temp = { ...showTitleEditor.value };
  showTitleEditor.value = temp;
}

function onDragEnd() {
  drag.value = false;
}

// ===============================================================
// Ingredient Linker
const activeRefs = ref<string[]>([]);
const activeIndex = ref(0);
const activeText = ref("");

function openDialog(idx: number, text: string, refs?: IngredientReferences[]) {
  if (!refs) {
    instructionList.value[idx].ingredientReferences = [];
    refs = instructionList.value[idx].ingredientReferences as IngredientReferences[];
  }

  setUsedIngredients();
  activeText.value = text;
  activeIndex.value = idx;
  dialog.value = true;
  activeRefs.value = refs.map(ref => ref.referenceId ?? "");
}

const availableNextStep = computed(() => activeIndex.value < instructionList.value.length - 1);

function setIngredientIds() {
  const instruction = instructionList.value[activeIndex.value];
  instruction.ingredientReferences = activeRefs.value.map((ref) => {
    return {
      referenceId: ref,
    };
  });

  // Update the visibility of the cook mode button
  showCookMode.value = false;
  instructionList.value.forEach((element) => {
    if (showCookMode.value === false && element.ingredientReferences && element.ingredientReferences.length > 0) {
      showCookMode.value = true;
    }
  });
  dialog.value = false;
}

function saveAndOpenNextLinkIngredients() {
  const currentStepIndex = activeIndex.value;

  if (!availableNextStep.value) {
    return; // no next step, the button calling this function should not be shown
  }

  setIngredientIds();
  const nextStep = instructionList.value[currentStepIndex + 1];
  // close dialog before opening to reset the scroll position
  nextTick(() => openDialog(currentStepIndex + 1, nextStep.text, nextStep.ingredientReferences));
}

function setUsedIngredients() {
  const usedRefs: { [key: string]: boolean } = {};

  instructionList.value.forEach((element) => {
    element.ingredientReferences?.forEach((ref) => {
      if (ref.referenceId !== undefined) {
        usedRefs[ref.referenceId!] = true;
      }
    });
  });

  usedIngredients.value = props.recipe.recipeIngredient.filter((ing) => {
    return ing.referenceId !== undefined && ing.referenceId in usedRefs;
  });

  unusedIngredients.value = props.recipe.recipeIngredient.filter((ing) => {
    return !(ing.referenceId !== undefined && ing.referenceId in usedRefs);
  });
}

function autoSetReferences() {
  useExtractIngredientReferences(
    props.recipe.recipeIngredient,
    activeRefs.value,
    activeText.value,
    props.recipe.settings.disableAmount,
  ).forEach((ingredient: string) => activeRefs.value.push(ingredient));
}

const ingredientLookup = computed(() => {
  const results: { [key: string]: RecipeIngredient } = {};
  return props.recipe.recipeIngredient.reduce((prev, ing) => {
    if (ing.referenceId === undefined) {
      return prev;
    }
    prev[ing.referenceId] = ing;
    return prev;
  }, results);
});

function getIngredientByRefId(refId: string | undefined) {
  if (refId === undefined) {
    return "";
  }

  const ing = ingredientLookup.value[refId];
  if (!ing) return "";
  return parseIngredientText(ing, props.recipe.settings.disableAmount, props.scale);
}

// ===============================================================
// Instruction Merger
const mergeHistory = ref<MergerHistory[]>([]);

function mergeAbove(target: number, source: number) {
  if (target < 0) {
    return;
  }

  mergeHistory.value.push({
    target,
    source,
    targetText: instructionList.value[target].text,
    sourceText: instructionList.value[source].text,
  });

  instructionList.value[target].text += " " + instructionList.value[source].text;
  instructionList.value.splice(source, 1);
}

function undoMerge(event: KeyboardEvent) {
  if (event.ctrlKey && event.code === "KeyZ") {
    if (!(mergeHistory.value?.length > 0)) {
      return;
    }

    const lastMerge = mergeHistory.value.pop();
    if (!lastMerge) {
      return;
    }

    instructionList.value[lastMerge.target].text = lastMerge.targetText;
    instructionList.value.splice(lastMerge.source, 0, {
      id: uuid4(),
      title: "",
      text: lastMerge.sourceText,
      ingredientReferences: [],
    });
  }
}

function moveTo(dest: string, source: number) {
  if (dest === "top") {
    instructionList.value.unshift(instructionList.value.splice(source, 1)[0]);
  }
  else {
    instructionList.value.push(instructionList.value.splice(source, 1)[0]);
  }
}

function insert(dest: number) {
  instructionList.value.splice(dest, 0, { id: uuid4(), text: "", title: "", ingredientReferences: [] });
}

const previewStates = ref<boolean[]>([]);

function togglePreviewState(index: number) {
  const temp = [...previewStates.value];
  temp[index] = !temp[index];
  previewStates.value = temp;
}

function toggleCollapseSection(index: number) {
  const sectionSteps: number[] = [];

  for (let i = index; i < instructionList.value.length; i++) {
    if (!(i === index) && hasSectionTitle(instructionList.value[i].title!)) {
      break;
    }
    else {
      sectionSteps.push(i);
    }
  }

  const allCollapsed = sectionSteps.every(idx => disabledSteps.value.includes(idx));

  if (allCollapsed) {
    disabledSteps.value = disabledSteps.value.filter(idx => !sectionSteps.includes(idx));
  }
  else {
    disabledSteps.value = [...disabledSteps.value, ...sectionSteps];
  }
}

const drag = ref(false);

// ===============================================================
// Image Uploader
const api = useUserApi();
const { recipeAssetPath } = useStaticRoutes();

const loadingStates = ref<{ [key: number]: boolean }>({});

async function handleImageDrop(index: number, files: File[]) {
  if (!files) {
    return;
  }

  // Check if the file is an image
  const file = files[0];
  if (!file || !file.type.startsWith("image/")) {
    return;
  }

  loadingStates.value[index] = true;

  const { data } = await api.recipes.createAsset(props.recipe.slug, {
    name: file.name,
    icon: "mdi-file-image",
    file,
    extension: file.name.split(".").pop() || "",
  });

  loadingStates.value[index] = false;

  if (!data) {
    return; // TODO: Handle error
  }

  emit("update:assets", [...assets.value, data]);
  const assetUrl = BASE_URL + recipeAssetPath(props.recipe.id, data.fileName as string);
  const text = `<img src="${assetUrl}" height="100%" width="100%"/>`;
  instructionList.value[index].text += text;
}

function openImageUpload(index: number) {
  const input = document.createElement("input");
  input.type = "file";
  input.accept = "image/*";
  input.onchange = async () => {
    if (input.files) {
      await handleImageDrop(index, Array.from(input.files));
      input.remove();
    }
  };
  input.click();
}
</script>

<style lang="css" scoped>
.v-card--link:before {
  background: none;
}

/** Select all li under .markdown class */
.markdown :deep(ul > li) {
  display: list-item;
  list-style-type: disc !important;
}

/** Select all li under .markdown class */
.markdown :deep(ol > li) {
  display: list-item;
}

.flip-list-move {
  transition: transform 0.5s;
}

.no-move {
  transition: transform 0s;
}

.ghost {
  opacity: 0.5;
}

.list-group {
  min-height: 38px;
}

.list-group-item i {
  cursor: pointer;
}

.blur {
  filter: blur(2px);
}

.upload-overlay {
  display: flex;
  justify-content: center;
  align-items: center;
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1;
}

.v-text-field >>> input {
  font-size: 1.5rem;
}
</style>
