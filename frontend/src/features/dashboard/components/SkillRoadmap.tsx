'use client';

/**
 * SkillRoadmap Component
 * スキルの進捗状況をツリー形式で表示
 */

import type { SkillNode } from '../types';

interface SkillRoadmapProps {
  skills: SkillNode[];
}

export function SkillRoadmap({ skills }: SkillRoadmapProps) {
  // ルートスキル（前提条件なし）を見つける
  const rootSkills = skills.filter((skill) => !skill.prerequisites || skill.prerequisites.length === 0);

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <h2 className="mb-8 text-2xl font-bold text-gray-900 dark:text-white">
        🛣️ スキルロードマップ
      </h2>

      <div className="space-y-6">
        {rootSkills.map((rootSkill) => (
          <SkillNode key={rootSkill.id} skill={rootSkill} allSkills={skills} />
        ))}
      </div>
    </div>
  );
}

interface SkillNodeProps {
  skill: SkillNode;
  allSkills: SkillNode[];
  depth?: number;
}

function SkillNode({ skill, allSkills, depth = 0 }: SkillNodeProps) {
  const childSkills = allSkills.filter(
    (s) => s.prerequisites?.includes(skill.id)
  );

  const marginLeft = `${depth * 2}rem`;

  return (
    <div style={{ marginLeft }}>
      <div
        className={`rounded-lg border-2 p-4 transition-all ${
          skill.completed
            ? 'border-green-500 bg-green-50 dark:border-green-600 dark:bg-green-900/20'
            : 'border-gray-300 bg-gray-50 dark:border-gray-600 dark:bg-gray-800'
        }`}
      >
        <div className="flex items-start gap-3">
          <div className="mt-1 text-3xl">{skill.icon}</div>
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <h3 className="font-semibold text-gray-900 dark:text-white">
                {skill.name}
              </h3>
              {skill.completed && (
                <span className="inline-flex items-center rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-800 dark:bg-green-900/30 dark:text-green-300">
                  ✓ 完了
                </span>
              )}
            </div>
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
              {skill.description}
            </p>
            {skill.completed && (
              <div className="mt-3 flex items-center gap-2">
                <div className="h-2 w-40 overflow-hidden rounded-full bg-gray-300 dark:bg-gray-600">
                  <div
                    className="h-full bg-gradient-to-r from-green-400 to-green-500"
                    style={{ width: `${skill.level * 20}%` }}
                  />
                </div>
                <span className="text-xs font-medium text-gray-600 dark:text-gray-400">
                  Lv. {skill.level}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 子スキル */}
      {childSkills.length > 0 && (
        <div className="mt-4 space-y-4">
          {childSkills.map((childSkill) => (
            <SkillNode
              key={childSkill.id}
              skill={childSkill}
              allSkills={allSkills}
              depth={depth + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
}
