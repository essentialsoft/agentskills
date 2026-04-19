import { createBrowserRouter } from "react-router-dom";
import App from "./App";
import { CatalogPage } from "./pages/CatalogPage";
import { SkillDetailPage } from "./pages/SkillDetailPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      {
        index: true,
        element: <CatalogPage />,
      },
      {
        path: "skills/:name",
        element: <SkillDetailPage />,
      },
    ],
  },
]);
