from dotenv import load_dotenv
import os
from document_processor import extract_text_from_pdf
from sales_agent import SalesAgent
from technical_agent import TechnicalAgent
from pricing_agent import PricingAgent
from pdf_exporter import create_proposal_pdf
from langchain_groq import ChatGroq

load_dotenv()



class OrchestratorAgent:
    """Coordinates Sales, Technical and Pricing agents, validates outputs, polishes text, and assembles the final proposal."""

    def run_and_export(self, pdf_path: str, output_file: str) -> dict:
        proposal = self.run(pdf_path)
        print("[4/4] Orchestrator: creating proposal PDF...")
        create_proposal_pdf(proposal, output_file)
        return proposal

    def __init__(self, model_name: str = "gpt-4o-mini"):
        self.sales = SalesAgent()
        self.tech = TechnicalAgent()
        self.pricing = PricingAgent()
        self.polish_llm = ChatGroq(temperature=0, model=model_name)

    def _validate(self, proposal: dict) -> list:
        issues = []
        if not proposal.get('requirements'):
            issues.append('No requirements extracted')
        if not proposal.get('technical_mapping'):
            issues.append('No technical mapping available')
        if not proposal.get('pricing'):
            issues.append('No pricing estimates available')
        return issues

    def _polish_section(self, title: str, content: str) -> str:
        prompt = (
            f"You are a senior proposal writer. Expand and enrich the following section titled '{title}' for clarity, professionalism, and persuasive impact. "
            "Add best practices, methodology, value propositions, and real-world examples relevant to the section. Use 3-5 paragraphs, include industry insights, and make the content visually engaging and comprehensive for a client proposal.\n\n" + content
        )
        try:
            resp = self.polish_llm(prompt)
            text = resp.generations[0][0].text if hasattr(resp, 'generations') else str(resp)
            return text.strip()
        except Exception:
            return content

    def run(self, pdf_path: str) -> dict:
        text = extract_text_from_pdf(pdf_path)

        print("[1/4] Sales Agent: extracting and summarizing...")
        rfp_summary = self.sales.analyze(text)

        print("[2/4] Technical Agent: mapping requirements...")
        tech_mapping = self.tech.map_requirements(rfp_summary.get("requirements", []))

        print("[3/4] Pricing Agent: estimating costs...")
        pricing_report = self.pricing.estimate(rfp_summary.get("requirements", []))

        proposal = {
            "client": rfp_summary.get("client", "Unknown Client"),
            "summary": rfp_summary.get("summary", ""),
            "requirements": rfp_summary.get("requirements", []),
            "technical_mapping": tech_mapping,
            "pricing": pricing_report,
        }

        issues = self._validate(proposal)
        if issues:
            proposal['_validation_issues'] = issues

        # Build sections
        sections = self.build_sections(proposal)

        # Polish each section for better readability
        polished_sections = []
        for sec in sections:
            polished = self._polish_section(sec['title'], sec['content'])
            polished_sections.append({'title': sec['title'], 'content': polished})

        proposal['sections'] = polished_sections

        return proposal

    def build_sections(self, proposal: dict) -> list:
        sections = []

        # I. Executive Summary
        exec_summary = proposal.get("summary") or "We propose a tailored IT solution to meet the client's objectives."
        company_name = os.getenv("COMPANY_NAME", "Vortex Solutions")
        company_mission = os.getenv("COMPANY_MISSION", "At Vortex Solutions, our mission is to empower organizations by transforming complex IT infrastructure into a strategic asset. We combine engineering excellence with unwavering delivery discipline to provide secure, scalable, and proactive managed services. By bridging the gap between legacy systems and future-ready technology, we ensure our partners can focus on their core mission while we manage the digital engine that drives their success.")
        company_vision = os.getenv("COMPANY_VISION", "To be the global benchmark for trust and innovation in IT Managed Services, recognized for fostering a security-first culture and engineering excellence. We envision a future where technology is never a barrier to progress, but a seamless, invisible force that enables organizations to reach their highest potential with absolute reliability.")
        company_approach = os.getenv("COMPANY_APPROACH", "We believe that every client is unique. Our solutions are tailored to your specific needs, ensuring that you receive maximum value from your IT investments. From initial consultation to final delivery, we prioritize transparency, communication, and measurable results.")
        company_results = os.getenv("COMPANY_RESULTS", "Our track record includes successful projects for public sector agencies, non-profits, and enterprises. We leverage best-in-class methodologies and the latest technology to deliver on time and on budget.")
        exec_content = (
            f"{exec_summary}\n\n"
            f"**Mission Statement**\n{company_mission}\n\n"
            f"**Vision Statement**\n{company_vision}\n\n"
            f"**Client-Centric Approach**\n{company_approach}\n\n"
            f"**Proven Results**\n{company_results}"
        )
        sections.append({"title": "I. Executive Summary", "content": exec_content})

        # II. The Problem
        reqs = proposal.get("requirements", [])
        if reqs:
            problems = "\n".join([f"- {r.get('text','')[:600]}" for r in reqs])
            problem_content = (
                "The RFP identifies the following objectives and constraints:\n"
                f"{problems}\n\n"
                "**Industry Challenges**\n"
                "Organizations today face unprecedented challenges: rapid technological change, increasing security threats, and the need to do more with less. "
                "Legacy systems, fragmented processes, and resource constraints can hinder progress.\n\n"
                "**Client-Specific Pain Points**\n"
                "Through our analysis, we have identified key pain points that must be addressed to achieve your goals. Our approach is designed to resolve these issues and unlock new opportunities for growth."
            )
        else:
            problem_content = (
                "The RFP highlights key needs and constraints that will be addressed by our solution.\n\n"
                "**Industry Challenges**\n"
                "Organizations today face unprecedented challenges: rapid technological change, increasing security threats, and the need to do more with less. "
                "Legacy systems, fragmented processes, and resource constraints can hinder progress.\n\n"
                "**Client-Specific Pain Points**\n"
                "Through our analysis, we have identified key pain points that must be addressed to achieve your goals. Our approach is designed to resolve these issues and unlock new opportunities for growth."
            )
        sections.append({"title": "II. The Problem", "content": problem_content})

        # III. Our Hi-Tech Solution
        tech_map = proposal.get('technical_mapping', [])
        if tech_map:
            solutions = []
            for m in tech_map:
                sid = m.get('requirement_id', '')
                services = ', '.join(m.get('services', []))
                approach = m.get('approach', '')
                compliance = m.get('compliance_score', m.get('compliance', ''))
                solutions.append(
                    f"**Requirement {sid}**\n"
                    f"- Services: {services}\n"
                    f"- Approach: {approach}\n"
                    f"- Compliance Score: {compliance}\n"
                )
            solution_content = (
                "Our solution leverages the latest advancements in cloud, automation, and security.\n\n"
                + "\n\n".join(solutions) +
                "\n\n**Technology Stack**\n"
                "We utilize industry-leading platforms and tools, ensuring scalability, security, and future-proofing. Our engineers are certified in AWS, Azure, and Google Cloud, and we maintain partnerships with top technology vendors.\n\n"
                "**Implementation Methodology**\n"
                "Our phased approach includes discovery, design, implementation, and ongoing support. We use agile project management to ensure flexibility and rapid delivery."
            )
        else:
            solution_content = (
                "We propose a proven technical approach leveraging cloud, automation, and security best practices.\n\n"
                "**Technology Stack**\n"
                "We utilize industry-leading platforms and tools, ensuring scalability, security, and future-proofing. Our engineers are certified in AWS, Azure, and Google Cloud, and we maintain partnerships with top technology vendors.\n\n"
                "**Implementation Methodology**\n"
                "Our phased approach includes discovery, design, implementation, and ongoing support. We use agile project management to ensure flexibility and rapid delivery."
            )
        sections.append({"title": "III. Our Hi-Tech Solution", "content": solution_content})

        # IV. Who We Are
        who_company = os.getenv("COMPANY_NAME", "Vortex Solutions")
        who_heritage = os.getenv("COMPANY_HERITAGE", "Founded on the principles of technical innovation and unwavering reliability, Vortex Solutions has evolved into a premier partner for organizations navigating the complexities of the modern digital landscape. Our mission is to empower our clients by bridging the gap between legacy infrastructure and future-ready technology. With a proven track record supporting complex agencies like the Mountains Recreation and Conservation Authority, we bring decades of collective experience to ensure that technical transformation serves as a powerful engine for your organizational goals.")
        who_engineering = os.getenv("COMPANY_ENGINEERING", "At the heart of our operations is a commitment to 'Engineering Excellence.' This is a technical standard that governs how we manage your critical assets, including the 112 PCs, 4 Dell PowerEdge Servers, and 5 SonicWALL Firewalls identified in your scope. We employ a data-driven approach to infrastructure management, ensuring that every environment is optimized for peak performance, scalability, and maximum uptime. Our senior engineers hold top-tier certifications to ensure that the technical advice we provide is rooted in current global industry best practices.")
        who_delivery = os.getenv("COMPANY_DELIVERY", "We recognize that agility is just as important as stability. Our 'Delivery Discipline' framework ensures that we meet aggressive timelines through a structured Project Management Office (PMO) approach. We utilize high-fidelity methodologies to provide transparent, real-time reporting and consistent quality targets. We do not just solve problems; we deliver validated solutions within the agreed-upon windows, ensuring that your operations across all 11 locations remain uninterrupted during critical maintenance or transition periods.")
        who_security = os.getenv("COMPANY_SECURITY", "In an era of sophisticated cyber threats, security is never an 'add-on'—it is integrated into the foundation of every service we provide. Our security-first culture means that encryption, identity management, and proactive threat hunting are standard components of our Managed Services. We adhere to rigorous standards, providing our clients with enterprise-grade protection that secures every endpoint, from onsite servers to the 40 remote access users in your fleet.")
        who_partnership = os.getenv("COMPANY_PARTNERSHIP", "We view our clients not as customers, but as strategic partners. Our engagement model is built on transparency, proactive communication, and shared success. By choosing Vortex Solutions, you are gaining a dedicated extension of your internal team—one that is committed to your long-term roadmap. We take the time to understand your unique operational culture, ensuring that our IT solutions integrate seamlessly with your existing human workflows.")
        who_content = (
            f"{who_company} is a seasoned IT services provider with deep experience in cloud migration, managed services, and security. "
            "We combine engineering excellence with delivery discipline to meet aggressive timelines and quality targets.\n\n"
            f"**Our Heritage & Mission**\n{who_heritage}\n\n"
            f"**Engineering Excellence**\n{who_engineering}\n\n"
            f"**Delivery Discipline**\n{who_delivery}\n\n"
            f"**Our Security-First Culture**\n{who_security}\n\n"
            f"**Strategic Partnership Philosophy**\n{who_partnership}"
        )
        sections.append({"title": "IV. Who We Are", "content": who_content})

        # V. Timeline and Pricing
        pricing = proposal.get('pricing', {})
        total_hours = pricing.get('total_hours', 0)
        weeks = max(1, int((total_hours / 40) or 1))
        timeline = f"Estimated delivery timeline: approximately {weeks} weeks (based on {total_hours} total hours)."
        scenarios = pricing.get('scenarios', {})
        pricing_lines = f"Scenarios - Baseline: ${scenarios.get('baseline',0)}, Competitive: ${scenarios.get('competitive',0)}, Premium: ${scenarios.get('premium',0)}"
        pricing_content = (
            f"{timeline}\n\n"
            "**Pricing Methodology**\n"
            "Our pricing is based on a transparent, activity-based costing model. Each requirement is carefully estimated for effort, complexity, and risk. "
            "We offer three pricing scenarios—baseline, competitive, and premium—so you can select the best fit for your budget and risk profile.\n\n"
            f"{pricing_lines}\n\n"
            "**What’s Included**\n"
            "All scenarios include project management, technical implementation, documentation, and post-go-live support. Optional services such as advanced security, training, and extended support are available upon request."
        )
        sections.append({"title": "V. Timeline and Pricing", "content": pricing_content})

        # VI. Your Return on Investment
        baseline_cost = scenarios.get('baseline', 0)
        annual_benefit = baseline_cost * 1.5 if baseline_cost else 0
        if annual_benefit > 0:
            payback_months = round((baseline_cost / (annual_benefit / 12)), 1)
            roi_content = (
                f"Estimated annual benefit: ${annual_benefit:.2f}. Estimated payback period: {payback_months} months.\n\n"
                "**Value Drivers**\n"
                "Our solution delivers value through cost savings, improved efficiency, and risk reduction. By modernizing your IT environment, you can expect lower maintenance costs, fewer outages, and faster response to business needs.\n\n"
                "**Long-Term Impact**\n"
                "Beyond immediate savings, our approach positions your organization for long-term growth. You will benefit from increased agility, better compliance, and a stronger security posture."
            )
        else:
            roi_content = (
                "Estimated ROI to be determined during scoping; we will provide a detailed financial model during Phase 1.\n\n"
                "**Value Drivers**\n"
                "Our solution delivers value through cost savings, improved efficiency, and risk reduction. By modernizing your IT environment, you can expect lower maintenance costs, fewer outages, and faster response to business needs.\n\n"
                "**Long-Term Impact**\n"
                "Beyond immediate savings, our approach positions your organization for long-term growth. You will benefit from increased agility, better compliance, and a stronger security posture."
            )
        sections.append({"title": "VI. Your Return on Investment", "content": roi_content})

        # VII. Terms and Conditions
        terms = (
            "Standard terms and conditions apply. All timelines and costs are estimates and subject to final scoping. "
            "A formal Statement of Work (SoW) and Master Services Agreement (MSA) will be provided upon request.\n\n"
            "**Confidentiality**\n"
            "All information shared between parties will be treated as confidential and used solely for the purposes of this engagement.\n\n"
            "**Change Management**\n"
            "Any changes to scope, timeline, or pricing will be managed through a formal change control process.\n\n"
            "**Governing Law**\n"
            "This proposal is governed by the laws of the applicable jurisdiction."
        )
        sections.append({"title": "VII. Terms and Conditions", "content": terms})

        # Optionally add a References section if citations are present
        references = os.getenv("COMPANY_REFERENCES", "[1] Example Reference 1\n[2] Example Reference 2\n[3] Example Reference 3\n[4] Example Reference 4\n[5] Example Reference 5")
        # Check for [cite: in any section content
        if any('[cite:' in sec['content'] for sec in sections):
            sections.append({"title": "VIII. References", "content": references})
        return sections