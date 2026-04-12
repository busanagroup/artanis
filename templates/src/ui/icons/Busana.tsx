import React from 'react'

export default function Busana({ ...props }: React.ComponentProps<'svg'>) {
  return (
    <svg
      viewBox="18 18 150 140"
      xmlns="http://www.w3.org/2000/svg"
      className="h-full w-full"
      {...props}
    >
      <path
        fill="#0c395d"
        fillRule="evenodd"
        stroke="#0c395d"
        strokeWidth=".462"
        d="M101.62 22.74c-.901.069-1.881.835-2.905 2.391-8.258 12.548-3.589 24.716-15.257 67.639-3.268 12.019-11.053 26.424-22.317 39.638-18.25 21.41-41.838 39.695-41.826 39.645 92.465-29.247 94.216-150.22 82.305-149.31z"
     />
      <path
        fill="#fec240"
        fillRule="evenodd"
        stroke="#fec240"
        d="M166.27 137.32c-47.117 16.823-63.761-7.635-68.871-37.786-7.267-42.877 13.315-92.62.248-72.776-13.009 19.753-18.909 54.393-10.751 87.913 6.692 27.499 24.374 40.493 42.936 39.773 27.069-1.05 36.438-17.124 36.438-17.124z"
      />
    </svg>
  )
}
