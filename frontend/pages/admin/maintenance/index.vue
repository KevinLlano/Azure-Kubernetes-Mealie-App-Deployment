<template>
  <v-container fluid class="narrow-container">
    <BaseDialog v-model="state.storageDetails" :title="$t('admin.maintenance.storage-details')"
      :icon="$globals.icons.folderOutline"
>
      <div class="py-2">
        <template v-for="(value, key, idx) in storageDetails" :key="`item-${key}`">
          <v-list-item>
            <v-list-item-title>
              <div>{{ storageDetailsText(key) }}</div>
            </v-list-item-title>
            <v-list-item-subtitle class="text-end">
              {{ value }}
            </v-list-item-subtitle>
          </v-list-item>
          <v-divider v-if="idx != 4" :key="`divider-${key}`" class="mx-2" />
        </template>
      </div>
    </BaseDialog>

    <BasePageTitle divider>
      <template #title>
        {{ $t("admin.maintenance.page-title") }}
      </template>
    </BasePageTitle>

    <section>
      <BaseCardSectionTitle class="pb-0" :icon="$globals.icons.wrench" :title="$t('admin.maintenance.summary-title')" />
      <div class="mb-6 d-flex" style="gap: 0.3rem">
        <BaseButton color="info" @click="getSummary">
          <template #icon>
            {{ $globals.icons.tools }}
          </template>
          {{ $t("admin.maintenance.button-label-get-summary") }}
        </BaseButton>
        <BaseButton color="info" @click="openDetails">
          <template #icon>
            {{ $globals.icons.folderOutline }}
          </template>
          {{ $t("admin.maintenance.button-label-open-details") }}
        </BaseButton>
      </div>
      <v-card class="" :loading="state.fetchingInfo">
        <template v-for="(value, idx) in info" :key="`item-${idx}`">
          <v-list-item>
            <v-list-item-title class="py-2">
              <div>{{ value.name }}</div>
              <v-list-item-subtitle class="text-end">
                {{ value.value }}
              </v-list-item-subtitle>
            </v-list-item-title>
          </v-list-item>
          <v-divider class="mx-2" />
        </template>
      </v-card>
    </section>
    <section>
      <BaseCardSectionTitle class="pb-0 mt-8" :icon="$globals.icons.wrench"
        :title="$t('admin.mainentance.actions-title')"
>
        <i18n-t keypath="admin.maintenance.actions-description">
          <template #destructive_in_bold>
            <b>{{ $t("admin.maintenance.actions-description-destructive") }}</b>
          </template>
          <template #irreversible_in_bold>
            <b>{{ $t("admin.maintenance.actions-description-irreversible") }}</b>
          </template>
        </i18n-t>
      </BaseCardSectionTitle>
      <v-card class="ma-0" flat :loading="state.actionLoading">
        <template v-for="(action, idx) in actions" :key="`item-${idx}`">
          <v-list-item class="py-2 px-0">
            <v-list-item-title>
              <div>{{ action.name }}</div>
              <v-list-item-subtitle class="wrap-word">
                {{ action.subtitle }}
              </v-list-item-subtitle>
            </v-list-item-title>
            <template #append>
              <BaseButton color="info" @click="action.handler">
              <template #icon>
                {{ $globals.icons.robot }}
              </template>
              {{ $t("general.run") }}
            </BaseButton>
            </template>
          </v-list-item>
          <v-divider class="mx-2" />
        </template>
      </v-card>
    </section>
  </v-container>
</template>

<script lang="ts">
import { useAdminApi } from "~/composables/api";
import type { MaintenanceStorageDetails, MaintenanceSummary } from "~/lib/api/types/admin";

export default defineNuxtComponent({
  setup() {
    definePageMeta({
      layout: "admin",
    });

    const state = reactive({
      storageDetails: false,
      storageDetailsLoading: false,
      fetchingInfo: false,
      actionLoading: false,
    });

    const adminApi = useAdminApi();
    const i18n = useI18n();

    // Set page title
    useSeoMeta({
      title: i18n.t("admin.maintenance.page-title"),
    });

    // ==========================================================================
    // General Info

    const infoResults = ref<MaintenanceSummary>({
      dataDirSize: i18n.t("about.unknown-version"),
      cleanableDirs: 0,
      cleanableImages: 0,
    });

    async function getSummary() {
      state.fetchingInfo = true;
      const { data } = await adminApi.maintenance.getInfo();

      infoResults.value = data ?? {
        dataDirSize: i18n.t("about.unknown-version"),
        cleanableDirs: 0,
        cleanableImages: 0,
      };

      state.fetchingInfo = false;
    }

    const info = computed(() => {
      return [
        {
          name: i18n.t("admin.maintenance.info-description-data-dir-size"),
          value: infoResults.value.dataDirSize,
        },
        {
          name: i18n.t("admin.maintenance.info-description-cleanable-directories"),
          value: infoResults.value.cleanableDirs,
        },
        {
          name: i18n.t("admin.maintenance.info-description-cleanable-images"),
          value: infoResults.value.cleanableImages,
        },
      ];
    });

    // ==========================================================================
    // Storage Details

    const storageTitles: { [key: string]: string } = {
      tempDirSize: i18n.t("admin.maintenance.storage.title-temporary-directory") as string,
      backupsDirSize: i18n.t("admin.maintenance.storage.title-backups-directory") as string,
      groupsDirSize: i18n.t("admin.maintenance.storage.title-groups-directory") as string,
      recipesDirSize: i18n.t("admin.maintenance.storage.title-recipes-directory") as string,
      userDirSize: i18n.t("admin.maintenance.storage.title-user-directory") as string,
    };

    function storageDetailsText(key: string) {
      return storageTitles[key] ?? i18n.t("about.unknown-version");
    }

    const storageDetails = ref<MaintenanceStorageDetails | null>(null);

    async function openDetails() {
      state.storageDetailsLoading = true;
      state.storageDetails = true;

      const { data } = await adminApi.maintenance.getStorageDetails();

      if (data) {
        storageDetails.value = data;
      }

      state.storageDetailsLoading = true;
    }

    // ==========================================================================
    // Actions

    async function handleCleanDirectories() {
      state.actionLoading = true;
      await adminApi.maintenance.cleanRecipeFolders();
      state.actionLoading = false;
    }

    async function handleCleanImages() {
      state.actionLoading = true;
      await adminApi.maintenance.cleanImages();
      state.actionLoading = false;
    }

    async function handleCleanTemp() {
      state.actionLoading = true;
      await adminApi.maintenance.cleanTemp();
      state.actionLoading = false;
    }

    const actions = [
      {
        name: i18n.t("admin.maintenance.action-clean-directories-name"),
        handler: handleCleanDirectories,
        subtitle: i18n.t("admin.maintenance.action-clean-directories-description"),
      },
      {
        name: i18n.t("admin.maintenance.action-clean-temporary-files-name"),
        handler: handleCleanTemp,
        subtitle: i18n.t("admin.maintenance.action-clean-temporary-files-description"),
      },
      {
        name: i18n.t("admin.maintenance.action-clean-images-name"),
        handler: handleCleanImages,
        subtitle: i18n.t("admin.maintenance.action-clean-images-description"),
      },
    ];

    return {
      storageDetailsText,
      openDetails,
      storageDetails,
      state,
      info,
      getSummary,
      actions,
    };
  },
});
</script>

<style scoped>
.wrap-word {
  white-space: normal;
  word-wrap: break-word;
}
</style>
