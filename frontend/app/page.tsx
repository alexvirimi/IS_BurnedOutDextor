"use client";

import Link from "next/link";
import { MicrosoftIcon } from "@/components/icons";

export default function HomePage() {
  return (
    <div
      className="min-h-screen w-full bg-cover bg-center bg-no-repeat flex"
      style={{
        backgroundImage:
          "url('https://hebbkx1anhila5yf.public.blob.vercel-storage.com/background-home-6kpqa8ERssLTFhUMEfZHc1VlHFE2ay.png')",
      }}
    >
      {/* Left Content */}
      <div className="flex-1 flex flex-col justify-center px-12 lg:px-24">
        <h1 className="font-heading font-bold text-4xl lg:text-5xl xl:text-6xl uppercase leading-tight tracking-tight max-w-xl">
          <span className="text-foreground">TOMARTE UN</span>
          <br />
          <span className="text-foreground">MOMENTO </span>
          <span className="text-primary">NO ES</span>
          <br />
          <span className="text-primary">FALLAR</span>
          <span className="text-foreground">, ES </span>
          <span className="text-primary">CUIDARTE</span>
        </h1>

        <div className="mt-10">
          <Link
            href="/login"
            className="inline-flex items-center gap-3 bg-white text-foreground font-sans font-medium px-6 py-3 rounded-lg shadow-md hover:shadow-lg transition-shadow"
          >
            <MicrosoftIcon className="w-5 h-5" />
            <span>Ingresar con Outlook</span>
          </Link>
        </div>
      </div>

      <div className="hidden lg:block flex-1" />
    </div>
  );
}
