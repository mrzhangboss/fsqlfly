export const dva = {
  config: {
    onError(e: Event & { message: string }) {
      e.preventDefault();
      console.error(e.message);
    },
  },
};
