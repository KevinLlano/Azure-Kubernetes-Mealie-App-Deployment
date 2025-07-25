<template>
  <BaseDialog
    v-model="inviteDialog"
    :title="$t('profile.get-invite-link')"
    :icon="$globals.icons.accountPlusOutline"
    color="primary"
  >
    <v-container>
      <v-form class="mt-5">
        <v-select
          v-if="groups && groups.length"
          v-model="selectedGroup"
          :items="groups"
          item-title="name"
          item-value="id"
          :return-object="false"
          variant="filled"
          :label="$t('group.user-group')"
          :rules="[validators.required]"
        />
        <v-select
          v-if="households && households.length"
          v-model="selectedHousehold"
          :items="filteredHouseholds"
          item-title="name"
          item-value="id"
          :return-object="false"
          variant="filled"
          :label="$t('household.user-household')"
          :rules="[validators.required]"
        />
        <v-row>
          <v-col cols="9">
            <v-text-field
              v-model="generatedSignupLink"
              :label="$t('profile.invite-link')"
              type="text"
              readonly
              variant="filled"
            />
          </v-col>
          <v-col
            cols="3"
            class="pl-1 mt-3"
          >
            <AppButtonCopy
              :icon="false"
              color="info"
              :copy-text="generatedSignupLink"
              :disabled="generatedSignupLink"
            />
          </v-col>
        </v-row>
        <v-text-field
          v-model="sendTo"
          :label="$t('user.email')"
          :rules="[validators.email]"
          variant="outlined"
          @keydown.enter="sendInvite"
        />
      </v-form>
    </v-container>
    <template #custom-card-action>
      <BaseButton
        :disabled="!validEmail"
        :loading="loading"
        :icon="$globals.icons.email"
        @click="sendInvite"
      >
        {{ $t("group.invite") }}
      </BaseButton>
    </template>
  </BaseDialog>
</template>

<script lang="ts">
import { watchEffect } from "vue";
import { useUserApi } from "@/composables/api";
import BaseDialog from "~/components/global/BaseDialog.vue";
import AppButtonCopy from "~/components/global/AppButtonCopy.vue";
import BaseButton from "~/components/global/BaseButton.vue";
import { validators } from "~/composables/use-validators";
import { alert } from "~/composables/use-toast";
import type { GroupInDB } from "~/lib/api/types/user";
import type { HouseholdInDB } from "~/lib/api/types/household";
import { useGroups } from "~/composables/use-groups";
import { useAdminHouseholds } from "~/composables/use-households";

export default defineNuxtComponent({
  name: "UserInviteDialog",
  components: {
    BaseDialog,
    AppButtonCopy,
    BaseButton,
  },
  props: {
    modelValue: {
      type: Boolean,
      default: false,
    },
  },
  emits: ["update:modelValue"],
  setup(props, context) {
    const i18n = useI18n();
    const $auth = useMealieAuth();

    const isAdmin = computed(() => $auth.user.value?.admin);
    const token = ref("");
    const selectedGroup = ref<string | null>(null);
    const selectedHousehold = ref<string | null>(null);
    const groups = ref<GroupInDB[]>([]);
    const households = ref<HouseholdInDB[]>([]);
    const api = useUserApi();

    const fetchGroupsAndHouseholds = () => {
      if (isAdmin.value) {
        const groupsResponse = useGroups();
        const householdsResponse = useAdminHouseholds();
        watchEffect(() => {
          groups.value = groupsResponse.groups.value || [];
          households.value = householdsResponse.households.value || [];
        });
      }
    };

    const inviteDialog = computed<boolean>({
      get() {
        return props.modelValue;
      },
      set(val) {
        context.emit("update:modelValue", val);
      },
    });

    async function getSignupLink(group: string | null = null, household: string | null = null) {
      const payload = (group && household) ? { uses: 1, group_id: group, household_id: household } : { uses: 1 };
      const { data } = await api.households.createInvitation(payload);
      if (data) {
        token.value = data.token;
      }
    }

    const filteredHouseholds = computed(() => {
      if (!selectedGroup.value) return [];
      return households.value?.filter(household => household.groupId === selectedGroup.value);
    });

    function constructLink(token: string) {
      return token ? `${window.location.origin}/register?token=${token}` : "";
    }

    const generatedSignupLink = computed(() => {
      return constructLink(token.value);
    });

    // =================================================
    // Email Invitation
    const state = reactive({
      loading: false,
      sendTo: "",
    });

    async function sendInvite() {
      state.loading = true;
      if (!token.value) {
        getSignupLink(selectedGroup.value, selectedHousehold.value);
      }
      const { data } = await api.email.sendInvitation({
        email: state.sendTo,
        token: token.value,
      });

      if (data && data.success) {
        alert.success(i18n.t("profile.email-sent"));
      }
      else {
        alert.error(i18n.t("profile.error-sending-email"));
      }
      state.loading = false;
      inviteDialog.value = false;
    }

    const validEmail = computed(() => {
      if (state.sendTo === "") {
        return false;
      }
      const valid = validators.email(state.sendTo);

      // Explicit bool check because validators.email sometimes returns a string
      if (valid === true) {
        return true;
      }
      return false;
    });

    return {
      sendInvite,
      validators,
      validEmail,
      inviteDialog,
      getSignupLink,
      generatedSignupLink,
      selectedGroup,
      selectedHousehold,
      filteredHouseholds,
      groups,
      households,
      fetchGroupsAndHouseholds,
      ...toRefs(state),
      isAdmin,
    };
  },
  watch: {
    modelValue: {
      immediate: false,
      handler(val) {
        if (val && !this.isAdmin) {
          this.getSignupLink();
        }
      },
    },
    selectedHousehold(newVal) {
      if (newVal && this.selectedGroup) {
        this.getSignupLink(this.selectedGroup, this.selectedHousehold);
      }
    },
  },
  created() {
    this.fetchGroupsAndHouseholds();
  },
});
</script>
