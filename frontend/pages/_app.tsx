import type { AppProps } from "next/app";
import Providers from "../app/providers";
import { ThemeProvider } from "../components/providers/ThemeProvider";

export default function MyApp({
  Component,
  pageProps,
}: AppProps) {
  return (
    <ThemeProvider>
      <Providers>
        <Component {...pageProps} />
      </Providers>
    </ThemeProvider>
  );
}