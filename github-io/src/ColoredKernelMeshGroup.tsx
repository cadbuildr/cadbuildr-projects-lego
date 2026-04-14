import React from "react";
import {
  BufferGeometry,
  Float32BufferAttribute,
  Matrix4,
  Quaternion,
  Vector3,
  Euler,
} from "three";

import { CADBUILDR_KERNEL_API_BASE_URL, type KernelDag } from "@cadbuildr/cad-kernel-r3f";

type MeshFacesPayload = {
  vertices: number[];
  triangles: number[];
  normals?: number[];
};

type ViewerMeshEntry = {
  data: { faces: MeshFacesPayload };
  type: "mesh";
};

type PartInstancePayload = {
  hash: string;
  tf: number[];
  color?: [number, number, number];
};

type SerializedMeshPayload = {
  store: Record<string, ViewerMeshEntry>;
  partInstances?: PartInstancePayload[];
};

function geometryFromFaces(faces: MeshFacesPayload): BufferGeometry {
  const geometry = new BufferGeometry();
  geometry.setIndex(faces.triangles);
  geometry.setAttribute("position", new Float32BufferAttribute(faces.vertices, 3));
  if (faces.normals && faces.normals.length > 0) {
    geometry.setAttribute("normal", new Float32BufferAttribute(faces.normals, 3));
  } else {
    geometry.computeVertexNormals();
  }
  geometry.computeBoundingBox();
  return geometry;
}

function rgbCss(rgb: [number, number, number] | undefined): string {
  if (!rgb) {
    return "#a8b0c0";
  }
  const [r, g, b] = rgb;
  return `rgb(${Math.round(r * 255)}, ${Math.round(g * 255)}, ${Math.round(b * 255)})`;
}

export type ColoredKernelMeshGroupProps = {
  dag: KernelDag;
  position: [number, number, number];
  rotation: [number, number, number];
  fetchImpl?: typeof fetch;
  onError?: (error: Error) => void;
  onLoaded?: () => void;
};

/** Renders kernel JSON mesh (per-instance colors); used when merged STL would lose brick colors. */
export function ColoredKernelMeshGroup({
  dag,
  position,
  rotation,
  fetchImpl,
  onError,
  onLoaded,
}: ColoredKernelMeshGroupProps): React.ReactElement | null {
  const [payload, setPayload] = React.useState<SerializedMeshPayload | null>(null);
  const fetchBound = fetchImpl ?? globalThis.fetch.bind(globalThis);
  const onErrorRef = React.useRef(onError);
  onErrorRef.current = onError;
  const onLoadedRef = React.useRef(onLoaded);
  onLoadedRef.current = onLoaded;

  React.useEffect(() => {
    setPayload(null);
    let cancelled = false;
    const controller = new AbortController();
    const url = `${CADBUILDR_KERNEL_API_BASE_URL.replace(/\/$/, "")}/v1/kernels/replicad/render`;

    async function load() {
      try {
        const response = await fetchBound(url, {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({
            dag,
            format: "json",
            kernel: "replicad",
          }),
          signal: controller.signal,
        });
        if (!response.ok) {
          throw new Error(`Kernel JSON mesh failed (${response.status})`);
        }
        const body = (await response.json()) as { format?: string; mesh?: SerializedMeshPayload };
        if (body.format !== "json" || !body.mesh) {
          throw new Error("Kernel response missing JSON mesh payload.");
        }
        if (!cancelled) {
          setPayload(body.mesh);
          onLoadedRef.current?.();
        }
      } catch (cause) {
        if (cancelled || (cause instanceof Error && cause.name === "AbortError")) {
          return;
        }
        const error = cause instanceof Error ? cause : new Error(String(cause));
        if (!cancelled) {
          setPayload(null);
          onErrorRef.current?.(error);
        }
      }
    }

    void load();
    return () => {
      cancelled = true;
      controller.abort();
    };
  }, [dag, fetchBound]);

  const items = React.useMemo(() => {
    if (!payload?.partInstances?.length) {
      return [];
    }
    return payload.partInstances
      .map((instance) => {
        const entry = payload.store[instance.hash];
        if (!entry || entry.type !== "mesh") {
          return null;
        }
        return {
          key: `${instance.hash}:${instance.tf.join(",")}`,
          geometry: geometryFromFaces(entry.data.faces),
          color: instance.color,
          matrix: new Matrix4().fromArray(instance.tf),
        };
      })
      .filter((item): item is NonNullable<typeof item> => item !== null);
  }, [payload]);

  React.useEffect(
    () => () => {
      for (const item of items) {
        item.geometry.dispose();
      }
    },
    [items]
  );

  const cadToScene = React.useMemo(() => {
    const euler = new Euler(rotation[0], rotation[1], rotation[2], "XYZ");
    const quat = new Quaternion().setFromEuler(euler);
    return new Matrix4().compose(
      new Vector3(position[0], position[1], position[2]),
      quat,
      new Vector3(1, 1, 1)
    );
  }, [position, rotation]);

  if (items.length === 0) {
    return null;
  }

  return (
    <>
      {items.map((item) => {
        const worldMatrix = cadToScene.clone().multiply(item.matrix);
        return (
          <group key={item.key} matrix={worldMatrix} matrixAutoUpdate={false}>
            <mesh geometry={item.geometry}>
              <meshStandardMaterial color={rgbCss(item.color)} metalness={0.1} roughness={0.45} />
            </mesh>
          </group>
        );
      })}
    </>
  );
}
