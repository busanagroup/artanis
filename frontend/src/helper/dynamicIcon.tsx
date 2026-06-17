import * as LucideIcons from "lucide-react";
import type { LucideIcon } from "lucide-react";

interface DynamicIconProps {
    name?: string;
    size?: number;
}

function lucideNameToComponent(name: string) {
    return name
        .split("-")
        .map(part => part.charAt(0).toUpperCase() + part.slice(1))
        .join("");
}

export function DynamicIcon({
    name,
    size = 18,
}: DynamicIconProps) {
    if (!name) return null;
    const componentName = lucideNameToComponent(name);
    const Icon = LucideIcons[
        componentName as keyof typeof LucideIcons
    ] as LucideIcon;

    if (!Icon) {
        return <LucideIcons.CircleHelp size={size} />;
    }

    return <Icon size={size} />;
}