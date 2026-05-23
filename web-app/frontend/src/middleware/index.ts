import { defineMiddleware } from "astro:middleware";
export const onRequest = defineMiddleware((context, next) => {
	console.log("request received at middleware:", context.request.url);

	return next();
});
