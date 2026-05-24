import { atom } from "nanostores";

export const isLoadingStore = atom<boolean>(false);

export const setIsLoading = (value: boolean) => isLoadingStore.set(value);
