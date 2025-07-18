<template>
  <v-container class="pa-0">
    <v-container>
      <BaseCardSectionTitle :title="$t('admin.debug-openai-services')">
        {{ $t('admin.debug-openai-services-description') }}
        <br>
        <DocLink
          class="mt-2"
          link="/documentation/getting-started/installation/open-ai"
        />
      </BaseCardSectionTitle>
    </v-container>
    <v-form
      ref="uploadForm"
      @submit.prevent="testOpenAI"
    >
      <div>
        <v-card-text>
          <v-container class="pa-0">
            <v-row>
              <v-col
                cols="auto"
                align-self="center"
              >
                <AppButtonUpload
                  v-if="!uploadedImage"
                  class="ml-auto"
                  url="none"
                  file-name="image"
                  accept="image/*"
                  :text="$t('recipe.upload-image')"
                  :text-btn="false"
                  :post="false"
                  @uploaded="uploadImage"
                />
                <v-btn
                  v-if="!!uploadedImage"
                  color="error"
                  @click="clearImage"
                >
                  <v-icon start>
                    {{ $globals.icons.close }}
                  </v-icon>
                  {{ $t("recipe.remove-image") }}
                </v-btn>
              </v-col>
              <v-spacer />
            </v-row>
            <v-row
              v-if="uploadedImage && uploadedImagePreviewUrl"
              style="max-width: 25%;"
            >
              <v-spacer />
              <v-col cols="12">
                <v-img :src="uploadedImagePreviewUrl" />
              </v-col>
              <v-spacer />
            </v-row>
          </v-container>
        </v-card-text>
        <v-card-actions>
          <BaseButton
            type="submit"
            :text="$t('admin.run-test')"
            :icon="$globals.icons.check"
            :loading="loading"
            class="ml-auto"
          />
        </v-card-actions>
      </div>
    </v-form>
    <v-divider
      v-if="response"
      class="mt-4"
    />
    <v-container
      v-if="response"
      class="ma-0 pa-0"
    >
      <v-card-title> {{ $t('admin.test-results') }} </v-card-title>
      <v-card-text> {{ response }} </v-card-text>
    </v-container>
  </v-container>
</template>

<script lang="ts">
import { useAdminApi } from "~/composables/api";
import { alert } from "~/composables/use-toast";

export default defineNuxtComponent({
  setup() {
    definePageMeta({
      layout: "admin",
    });

    const api = useAdminApi();
    const i18n = useI18n();

    // Set page title
    useSeoMeta({
      title: i18n.t("admin.debug-openai-services"),
    });

    const loading = ref(false);
    const response = ref("");

    const uploadForm = ref<VForm | null>(null);
    const uploadedImage = ref<Blob | File>();
    const uploadedImageName = ref<string>("");
    const uploadedImagePreviewUrl = ref<string>();

    function uploadImage(fileObject: File) {
      uploadedImage.value = fileObject;
      uploadedImageName.value = fileObject.name;
      uploadedImagePreviewUrl.value = URL.createObjectURL(fileObject);
    }

    function clearImage() {
      uploadedImage.value = undefined;
      uploadedImageName.value = "";
      uploadedImagePreviewUrl.value = undefined;
    }

    async function testOpenAI() {
      response.value = "";

      loading.value = true;
      const { data } = await api.debug.debugOpenAI(uploadedImage.value);
      loading.value = false;

      if (!data) {
        alert.error("Unable to test OpenAI services");
      }
      else {
        response.value = data.response || (data.success ? "Test Successful" : "Test Failed");
      }
    }

    return {
      loading,
      response,
      uploadForm,
      uploadedImage,
      uploadedImagePreviewUrl,
      uploadImage,
      clearImage,
      testOpenAI,
    };
  },
});
</script>
