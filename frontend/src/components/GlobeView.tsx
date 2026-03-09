"use client";

import { useRef, useMemo, useCallback, useEffect } from "react";
import { Canvas, useFrame, useThree, ThreeEvent } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import * as THREE from "three";
import { useNetworkStore } from "@/lib/store";
import type { NetworkNode, TrafficRoute } from "@/types/network";

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------
const GLOBE_RADIUS = 2;
const NODE_BASE_SIZE = 0.015;
const ARC_SEGMENTS = 48;

const STATUS_COLORS = {
  healthy: new THREE.Color(0x22c55e),
  degraded: new THREE.Color(0xf59e0b),
  failing: new THREE.Color(0xef4444),
  offline: new THREE.Color(0x64748b),
};

const TYPE_SIZES: Record<string, number> = {
  backbone: 1.8,
  ix_point: 1.6,
  cloud_region: 1.4,
  data_center: 1.2,
  isp: 1.0,
  satellite: 0.9,
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function latLngToVec3(lat: number, lng: number, radius: number): THREE.Vector3 {
  const phi = (90 - lat) * (Math.PI / 180);
  const theta = (lng + 180) * (Math.PI / 180);
  return new THREE.Vector3(
    -radius * Math.sin(phi) * Math.cos(theta),
    radius * Math.cos(phi),
    radius * Math.sin(phi) * Math.sin(theta)
  );
}

function makeArcCurve(
  start: THREE.Vector3,
  end: THREE.Vector3,
  radius: number
): THREE.QuadraticBezierCurve3 {
  const mid = new THREE.Vector3()
    .addVectors(start, end)
    .multiplyScalar(0.5)
    .normalize()
    .multiplyScalar(radius + 0.15 + start.distanceTo(end) * 0.12);
  return new THREE.QuadraticBezierCurve3(start, mid, end);
}

// ---------------------------------------------------------------------------
// Earth Sphere
// ---------------------------------------------------------------------------
function EarthSphere() {
  const meshRef = useRef<THREE.Mesh>(null);

  const material = useMemo(
    () =>
      new THREE.MeshPhongMaterial({
        color: 0x0c1525,
        emissive: 0x060d18,
        specular: 0x111827,
        shininess: 5,
        transparent: true,
        opacity: 0.95,
      }),
    []
  );

  return (
    <mesh ref={meshRef} material={material}>
      <sphereGeometry args={[GLOBE_RADIUS, 64, 64]} />
    </mesh>
  );
}

// ---------------------------------------------------------------------------
// Wireframe grid overlay
// ---------------------------------------------------------------------------
function GlobeGrid() {
  const geo = useMemo(() => {
    return new THREE.SphereGeometry(GLOBE_RADIUS + 0.002, 36, 18);
  }, []);

  return (
    <lineSegments>
      <wireframeGeometry args={[geo]} />
      <lineBasicMaterial color={0x1a2a3f} transparent opacity={0.3} />
    </lineSegments>
  );
}

// ---------------------------------------------------------------------------
// Atmosphere glow
// ---------------------------------------------------------------------------
function Atmosphere() {
  const material = useMemo(
    () =>
      new THREE.ShaderMaterial({
        vertexShader: `
          varying vec3 vNormal;
          void main() {
            vNormal = normalize(normalMatrix * normal);
            gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
          }
        `,
        fragmentShader: `
          varying vec3 vNormal;
          void main() {
            float intensity = pow(0.65 - dot(vNormal, vec3(0.0, 0.0, 1.0)), 2.5);
            gl_FragColor = vec4(0.15, 0.35, 0.65, 1.0) * intensity;
          }
        `,
        blending: THREE.AdditiveBlending,
        side: THREE.BackSide,
        transparent: true,
      }),
    []
  );

  return (
    <mesh material={material}>
      <sphereGeometry args={[GLOBE_RADIUS * 1.12, 32, 32]} />
    </mesh>
  );
}

// ---------------------------------------------------------------------------
// Infrastructure Nodes (instanced)
// ---------------------------------------------------------------------------
function InfrastructureNodes({ nodes }: { nodes: NetworkNode[] }) {
  const meshRef = useRef<THREE.InstancedMesh>(null);
  const setSelectedNode = useNetworkStore((s) => s.setSelectedNode);
  const tempObj = useMemo(() => new THREE.Object3D(), []);
  const tempColor = useMemo(() => new THREE.Color(), []);

  useEffect(() => {
    if (!meshRef.current || nodes.length === 0) return;

    const mesh = meshRef.current;
    nodes.forEach((node, i) => {
      const pos = latLngToVec3(node.lat, node.lng, GLOBE_RADIUS + 0.005);
      const scale = NODE_BASE_SIZE * (TYPE_SIZES[node.type] || 1);
      tempObj.position.copy(pos);
      tempObj.scale.setScalar(scale);
      tempObj.updateMatrix();
      mesh.setMatrixAt(i, tempObj.matrix);

      const color = STATUS_COLORS[node.status] || STATUS_COLORS.healthy;
      mesh.setColorAt(i, color);
    });
    mesh.instanceMatrix.needsUpdate = true;
    if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
  }, [nodes, tempObj]);

  // Pulse effect for degraded/failing nodes
  useFrame(({ clock }) => {
    if (!meshRef.current || nodes.length === 0) return;
    const t = clock.getElapsedTime();
    const mesh = meshRef.current;

    nodes.forEach((node, i) => {
      if (node.status === "degraded" || node.status === "failing") {
        const pulseSpeed = node.status === "failing" ? 4 : 2;
        const pulseScale = 1 + 0.3 * Math.sin(t * pulseSpeed);
        const baseScale = NODE_BASE_SIZE * (TYPE_SIZES[node.type] || 1);
        const pos = latLngToVec3(node.lat, node.lng, GLOBE_RADIUS + 0.005);
        tempObj.position.copy(pos);
        tempObj.scale.setScalar(baseScale * pulseScale);
        tempObj.updateMatrix();
        mesh.setMatrixAt(i, tempObj.matrix);
      }
    });
    mesh.instanceMatrix.needsUpdate = true;
  });

  const handleClick = useCallback(
    (e: ThreeEvent<MouseEvent>) => {
      e.stopPropagation();
      if (e.instanceId !== undefined && e.instanceId < nodes.length) {
        setSelectedNode(nodes[e.instanceId].id);
      }
    },
    [nodes, setSelectedNode]
  );

  if (nodes.length === 0) return null;

  return (
    <instancedMesh
      ref={meshRef}
      args={[undefined, undefined, nodes.length]}
      onClick={handleClick}
    >
      <sphereGeometry args={[1, 12, 12]} />
      <meshBasicMaterial toneMapped={false} />
    </instancedMesh>
  );
}

// ---------------------------------------------------------------------------
// Node glow halos for degraded/failing
// ---------------------------------------------------------------------------
function NodeHalos({ nodes }: { nodes: NetworkNode[] }) {
  const troubled = useMemo(
    () => nodes.filter((n) => n.status === "degraded" || n.status === "failing"),
    [nodes]
  );

  const meshRef = useRef<THREE.InstancedMesh>(null);
  const tempObj = useMemo(() => new THREE.Object3D(), []);

  useFrame(({ clock }) => {
    if (!meshRef.current || troubled.length === 0) return;
    const t = clock.getElapsedTime();

    troubled.forEach((node, i) => {
      const pos = latLngToVec3(node.lat, node.lng, GLOBE_RADIUS + 0.004);
      const expandRate = node.status === "failing" ? 5 : 3;
      const maxScale = node.status === "failing" ? 0.06 : 0.04;
      const scale = maxScale * (1 + 0.5 * Math.sin(t * expandRate));
      tempObj.position.copy(pos);
      tempObj.lookAt(0, 0, 0);
      tempObj.scale.setScalar(scale);
      tempObj.updateMatrix();
      meshRef.current!.setMatrixAt(i, tempObj.matrix);

      const color =
        node.status === "failing"
          ? new THREE.Color(0xef4444)
          : new THREE.Color(0xf59e0b);
      meshRef.current!.setColorAt(i, color);
    });
    meshRef.current!.instanceMatrix.needsUpdate = true;
    if (meshRef.current!.instanceColor)
      meshRef.current!.instanceColor.needsUpdate = true;
  });

  if (troubled.length === 0) return null;

  return (
    <instancedMesh
      ref={meshRef}
      args={[undefined, undefined, troubled.length]}
    >
      <ringGeometry args={[0.8, 1, 24]} />
      <meshBasicMaterial
        transparent
        opacity={0.25}
        side={THREE.DoubleSide}
        toneMapped={false}
      />
    </instancedMesh>
  );
}

// ---------------------------------------------------------------------------
// Traffic Arcs
// ---------------------------------------------------------------------------
function TrafficArcs({
  routes,
  nodes,
}: {
  routes: TrafficRoute[];
  nodes: NetworkNode[];
}) {
  const groupRef = useRef<THREE.Group>(null);

  const lineObjects = useMemo(() => {
    const nodeMap = new Map(nodes.map((n) => [n.id, n]));
    const lines: THREE.Line[] = [];

    // Limit arcs for performance
    const visibleRoutes = routes.filter((r) => r.active).slice(0, 400);

    for (const route of visibleRoutes) {
      const src = nodeMap.get(route.source_id);
      const dst = nodeMap.get(route.target_id);
      if (!src || !dst) continue;

      const startPos = latLngToVec3(src.lat, src.lng, GLOBE_RADIUS + 0.006);
      const endPos = latLngToVec3(dst.lat, dst.lng, GLOBE_RADIUS + 0.006);
      const curve = makeArcCurve(startPos, endPos, GLOBE_RADIUS);
      const points = curve.getPoints(ARC_SEGMENTS);
      const geo = new THREE.BufferGeometry().setFromPoints(points);

      // Color by utilization
      const util = route.utilization_pct;
      const color =
        util > 80
          ? new THREE.Color(0xef4444)
          : util > 60
          ? new THREE.Color(0xf59e0b)
          : new THREE.Color(0x3b82f6);
      color.multiplyScalar(0.5);

      const mat = new THREE.LineBasicMaterial({
        color,
        transparent: true,
        opacity: 0.35,
      });
      lines.push(new THREE.Line(geo, mat));
    }

    return lines;
  }, [routes, nodes]);

  if (lineObjects.length === 0) return null;

  return (
    <group ref={groupRef}>
      {lineObjects.map((obj, i) => (
        <primitive key={i} object={obj} />
      ))}
    </group>
  );
}

// ---------------------------------------------------------------------------
// Incident Rings (expanding rings at incident locations)
// ---------------------------------------------------------------------------
function IncidentRings() {
  const incidents = useNetworkStore((s) => s.incidents);
  const groupRef = useRef<THREE.Group>(null);

  if (incidents.length === 0) return null;

  return (
    <group ref={groupRef}>
      {incidents.slice(0, 10).map((inc) => (
        <IncidentRing key={inc.id} lat={inc.lat} lng={inc.lng} severity={inc.severity} />
      ))}
    </group>
  );
}

function IncidentRing({
  lat,
  lng,
  severity,
}: {
  lat: number;
  lng: number;
  severity: string;
}) {
  const meshRef = useRef<THREE.Mesh>(null);
  const pos = useMemo(() => latLngToVec3(lat, lng, GLOBE_RADIUS + 0.003), [lat, lng]);

  useFrame(({ clock }) => {
    if (!meshRef.current) return;
    const t = clock.getElapsedTime();
    const scale = 0.03 + 0.04 * ((t * 0.8) % 1);
    meshRef.current.scale.setScalar(scale);
    const mat = meshRef.current.material as THREE.MeshBasicMaterial;
    mat.opacity = 0.4 * (1 - ((t * 0.8) % 1));
  });

  const color = severity === "critical" ? 0xef4444 : severity === "high" ? 0xf97316 : 0xf59e0b;

  return (
    <mesh ref={meshRef} position={pos}>
      <ringGeometry args={[0.8, 1, 32]} />
      <meshBasicMaterial
        color={color}
        transparent
        opacity={0.4}
        side={THREE.DoubleSide}
        toneMapped={false}
      />
    </mesh>
  );
}

// ---------------------------------------------------------------------------
// Scene (auto-rotation)
// ---------------------------------------------------------------------------
function AutoRotate() {
  const { scene } = useThree();
  const globeGroup = useRef(scene);

  useFrame((_, delta) => {
    // Slow auto-rotation
    scene.rotation.y += delta * 0.02;
  });

  return null;
}

// ---------------------------------------------------------------------------
// Main Scene Content
// ---------------------------------------------------------------------------
function SceneContent() {
  const nodes = useNetworkStore((s) => s.nodes);
  const routes = useNetworkStore((s) => s.routes);

  return (
    <>
      {/* Lighting */}
      <ambientLight intensity={0.3} />
      <directionalLight position={[5, 3, 5]} intensity={0.8} color={0xd4e5ff} />
      <pointLight position={[-5, -3, -5]} intensity={0.3} color={0x4477aa} />

      {/* Globe */}
      <group>
        <EarthSphere />
        <GlobeGrid />
        <Atmosphere />
        <InfrastructureNodes nodes={nodes} />
        <NodeHalos nodes={nodes} />
        <TrafficArcs routes={routes} nodes={nodes} />
        <IncidentRings />
      </group>

      {/* Controls */}
      <OrbitControls
        enableDamping
        dampingFactor={0.05}
        minDistance={2.5}
        maxDistance={8}
        enablePan={false}
        rotateSpeed={0.5}
        zoomSpeed={0.8}
      />
    </>
  );
}

// ---------------------------------------------------------------------------
// Exported component
// ---------------------------------------------------------------------------
export default function GlobeView() {
  return (
    <div className="w-full h-full">
      <Canvas
        camera={{ position: [0, 0, 5], fov: 45, near: 0.1, far: 100 }}
        gl={{
          antialias: true,
          alpha: true,
          powerPreference: "high-performance",
        }}
        style={{ background: "transparent" }}
        dpr={[1, 2]}
      >
        <SceneContent />
      </Canvas>
    </div>
  );
}
