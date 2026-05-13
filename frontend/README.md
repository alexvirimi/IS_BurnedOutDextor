# Frontend

Interfaz web del proyecto `IS_BurnedOutDextor`, desarrollada con Next.js y React.

## Stack

- Next.js 16
- React 19
- Tailwind CSS 4
- pnpm

## Requisitos

- Node.js compatible con Next.js 16
- pnpm

## Instalación

```bash
cd frontend
pnpm install
```

## Ejecución en desarrollo

```bash
cd frontend
pnpm dev
```

Luego abre `http://localhost:3000`.

## Construcción

```bash
cd frontend
pnpm build
pnpm start
```

## Configuración

El frontend consume las APIs configuradas en `NEXT_PUBLIC_API_URL`.

Si usas Docker Compose, el frontend se expone en `http://localhost:3000`.
