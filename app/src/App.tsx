import './App.css'
import "@react-sigma/core/lib/react-sigma.min.css"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { Main } from "./Main.tsx";

function App() {
  const queryClient = new QueryClient()


  return (
    <QueryClientProvider client={queryClient}>
      <Main/>
      <ReactQueryDevtools initialIsOpen={false}/>
    </QueryClientProvider>
  )
}

export default App
