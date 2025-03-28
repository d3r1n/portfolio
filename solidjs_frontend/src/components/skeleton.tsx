import { JSX } from "solid-js";

export enum SkeletonComponent {
    Line,
    Circle,
    Rectangle,
}

interface SkeletonProps {
    classExtra?: Array<string>
}

export function SkeletonLine(props: SkeletonProps): JSX.Element {
    if (!props.classExtra) {
        props.classExtra = [
            "w-full", "h-4", "bg-neutral-300"
        ]
    }

    return (
        <>
            <div class={["skeleton--line rounded-md animate-pulse", ...props.classExtra].join(" ")} />
        </>
    );
}

export function SkeletonCircle(size: number = 24): JSX.Element {
    return (
        <>
            <div class={`skeleton--circle size-${size} rounded-full`} />
        </>
    );
}

export function SkeletonRectangle(props: SkeletonProps) {
    if (!props.classExtra) {
        props.classExtra = [
            "w-full", "h-full", "bg-neutral-300"
        ]
    }

    return (
        <>
            <div class={["skeleton--rectangle rounded-md animate-pulse", ...props.classExtra].join(" ")} />
        </>
    );
}