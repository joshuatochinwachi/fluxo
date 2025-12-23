import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-[#5B1A8B] text-white hover:bg-[#6A1BB1]",
        secondary:
          "border-transparent bg-[#F4F1F7] text-[#5B1A8B] dark:bg-[#8E3CC8]/20 dark:text-[#C77DFF] hover:bg-[#E3A8FF]/30",
        destructive:
          "border-transparent bg-destructive text-destructive-foreground hover:bg-destructive/80",
        outline: "border-[#8E3CC8]/30 text-[#8E3CC8] bg-transparent",
        success:
          "border-transparent bg-[#5B1A8B]/10 text-[#C77DFF]",
        warning:
          "border-transparent bg-[#E3A8FF]/20 text-[#8E3CC8]",
        danger:
          "border-transparent bg-destructive/10 text-destructive",
        signal:
          "border-transparent bg-[#E3A8FF]/30 text-[#5B1A8B] dark:text-[#E3A8FF]",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  )
}

export { Badge, badgeVariants }
